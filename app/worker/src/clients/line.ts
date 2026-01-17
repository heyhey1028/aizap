/**
 * LINE Messaging API クライアント
 *
 * LINE Push API を使用してユーザーにメッセージを送信する。
 */
import { messagingApi, TextMessage } from '@line/bot-sdk';
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
