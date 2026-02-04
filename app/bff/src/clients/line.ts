import { ClientConfig } from '@line/bot-sdk';
import * as line from '@line/bot-sdk';
import { getLineChannelAccessToken } from '@/config/env.js';

let lineClient: line.messagingApi.MessagingApiClient | null = null;

/**
 * LINE SDK クライアントを取得する。
 * 初回呼び出し時にクライアントを初期化し、以降は同じインスタンスを返す。
 *
 * @returns LINE SDK クライアントインスタンス
 * @throws {Error} 環境変数 LINE_CHANNEL_ACCESS_TOKEN が未設定の場合
 */
export function getLineClient(): line.messagingApi.MessagingApiClient {
  if (!lineClient) {
    const channelAccessToken = getLineChannelAccessToken();
    const config: ClientConfig = {
      channelAccessToken,
    };
    lineClient = new line.messagingApi.MessagingApiClient(config);
  }
  return lineClient;
}

/**
 * Reply API でテキストメッセージを返信する。
 *
 * @param replyToken 返信用トークン
 * @param text 返信するテキスト
 */
export async function replyMessage(
  replyToken: string,
  text: string
): Promise<void> {
  const client = getLineClient();
  await client.replyMessage({
    replyToken,
    messages: [{ type: 'text', text }],
  });
}

/**
 * 読み込み中アニメーションを表示する
 * @param userId LINE ユーザー ID
 */
export async function startLoading(userId: string): Promise<void> {
  const client = getLineClient();
  await client.showLoadingAnimation({
    chatId: userId,
    loadingSeconds: 60,
  });
}
