/**
 * GCS クライアント
 *
 * LINE の画像/動画/音声を GCS にアップロードする。
 */
import { Storage } from '@google-cloud/storage';
import { Readable } from 'node:stream';
import { pipeline } from 'node:stream/promises';
import { getMediaBucketName } from '@/config/env.js';
import { logger } from '@/utils/logger.js';
import type { MessageType } from '@/types/index.js';

let storage: Storage | null = null;

/**
 * Storage クライアントを取得する。
 *
 * @returns Storage クライアント
 */
function getStorage(): Storage {
  if (!storage) {
    storage = new Storage();
  }
  return storage;
}

export interface UploadLineContentParams {
  /** LINE ユーザー ID */
  userId: string;
  /** LINE メッセージ ID */
  messageId: string;
  /** メッセージタイプ */
  messageType: Extract<MessageType, 'image' | 'video' | 'audio'>;
  /** タイムスタンプ（ISO 8601 形式） */
  timestamp: string;
  /** Content-Type */
  contentType: string | null;
  /** コンテンツのストリーム */
  stream: Readable;
}

type ErrorWithCode = {
  code?: number;
};

/**
 * エラーに code が含まれているか判定する。
 *
 * @param error 判定対象のエラー
 * @returns code を持つ場合は true
 */
function isErrorWithCode(error: unknown): error is ErrorWithCode {
  return typeof error === 'object' && error !== null && 'code' in error;
}

function pad2(value: number): string {
  return value.toString().padStart(2, '0');
}

function resolveContentType(
  messageType: UploadLineContentParams['messageType'],
  contentType: string | null
): string {
  if (contentType) return contentType;
  if (messageType === 'image') return 'image/jpeg';
  if (messageType === 'audio') return 'audio/mpeg';
  return 'video/mp4';
}

function resolveExtension(contentType: string): string {
  const normalized = contentType.split(';')[0]?.trim().toLowerCase();
  switch (normalized) {
    case 'image/jpeg':
      return 'jpg';
    case 'image/png':
      return 'png';
    case 'image/gif':
      return 'gif';
    case 'image/webp':
      return 'webp';
    case 'video/mp4':
      return 'mp4';
    case 'audio/mpeg':
      return 'mp3';
    case 'audio/mp4':
      return 'm4a';
    case 'audio/m4a':
      return 'm4a';
    case 'audio/aac':
      return 'aac';
    case 'audio/ogg':
      return 'ogg';
    case 'audio/wav':
      return 'wav';
    default:
      return 'bin';
  }
}

function buildObjectName(
  params: UploadLineContentParams,
  extension: string
): string {
  const date = new Date(params.timestamp);
  if (Number.isNaN(date.getTime())) {
    return `line/${params.messageType}/user/${params.userId}/unknown/${params.messageId}.${extension}`;
  }

  const year = date.getUTCFullYear();
  const month = pad2(date.getUTCMonth() + 1);
  const day = pad2(date.getUTCDate());
  return `line/${params.messageType}/user/${params.userId}/${year}/${month}/${day}/${params.messageId}.${extension}`;
}

/**
 * LINE メッセージコンテンツを GCS にアップロードする。
 *
 * @param params アップロードに必要な情報
 * @returns GCS の gs:// URI
 */
export async function uploadLineContent(
  params: UploadLineContentParams
): Promise<string> {
  const bucketName = getMediaBucketName();
  const bucket = getStorage().bucket(bucketName);
  const resolvedContentType = resolveContentType(
    params.messageType,
    params.contentType
  );
  const extension = resolveExtension(resolvedContentType);
  const objectName = buildObjectName(params, extension);
  const file = bucket.file(objectName);

  try {
    await pipeline(
      params.stream,
      file.createWriteStream({
        metadata: {
          contentType: resolvedContentType,
        },
        preconditionOpts: {
          ifGenerationMatch: 0,
        },
      })
    );
    logger.info(
      { bucketName, objectName, userId: params.userId },
      'Uploaded LINE content to GCS'
    );
  } catch (error) {
    if (isErrorWithCode(error) && error.code === 412) {
      logger.info(
        { bucketName, objectName, userId: params.userId },
        'GCS object already exists'
      );
    } else {
      logger.error(
        { err: error, bucketName, objectName, userId: params.userId },
        'Failed to upload LINE content to GCS'
      );
      throw error;
    }
  }

  return `gs://${bucketName}/${objectName}`;
}
