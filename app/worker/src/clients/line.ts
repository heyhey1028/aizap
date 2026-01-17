/**
 * LINE Messaging API クライアント
 *
 * LINE Push API を使用してユーザーにメッセージを送信する。
 */
import { messagingApi, TextMessage } from '@line/bot-sdk';
import { Readable } from 'node:stream';
import { getLineChannelAccessToken } from '@/config/env.js';
import { logger } from '@/utils/logger.js';

let lineClient: messagingApi.MessagingApiClient | null = null;

/**
 * LINE クライアントを取得する。
 * シングルトンパターンで、初回呼び出し時にインスタンスを生成する。
 *
 * @returns LINE Messaging API クライアント
 */
export function getLineClient(): messagingApi.MessagingApiClient {
  if (!lineClient) {
    lineClient = new messagingApi.MessagingApiClient({
      channelAccessToken: getLineChannelAccessToken(),
    });
  }
  return lineClient;
}

export interface LineMessageContent {
  /** メッセージコンテンツのストリーム */
  stream: Readable;
  /** Content-Type */
  contentType: string | null;
}

/**
 * LINE Messaging API からメッセージコンテンツを取得する。
 *
 * @param messageId LINE メッセージ ID
 * @returns コンテンツのストリームと Content-Type
 */
export async function getMessageContent(
  messageId: string
): Promise<LineMessageContent> {
  const token = getLineChannelAccessToken();
  const response = await fetch(
    `https://api-data.line.me/v2/bot/message/${messageId}/content`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  if (!response.ok || !response.body) {
    logger.error(
      { messageId, status: response.status },
      'Failed to fetch LINE message content'
    );
    throw new Error('LINE message content fetch failed');
  }

  return {
    stream: Readable.fromWeb(response.body),
    contentType: response.headers.get('content-type'),
  };
}

/**
 * ユーザーに Push メッセージを送信する。
 *
 * @param userId 送信先の LINE ユーザー ID
 * @param text 送信するテキスト
 */
export async function pushMessage(userId: string, text: string): Promise<void> {
  const client = getLineClient();

  const message: TextMessage = {
    type: 'text',
    text,
  };

  try {
    await client.pushMessage({
      to: userId,
      messages: [message],
    });
    logger.info({ userId }, 'Sent push message to LINE');
  } catch (error) {
    logger.error({ userId, err: error }, 'Failed to send push message');
    throw error;
  }
}
