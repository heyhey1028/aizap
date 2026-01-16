import { Client, ClientConfig } from '@line/bot-sdk';
import { getLineChannelAccessToken } from '@/config/env.js';

/**
 * LINE SDK クライアントを初期化してエクスポートする。
 * シングルトンパターンでクライアントを管理する。
 */
let lineClient: Client | null = null;

/**
 * LINE SDK クライアントを取得する。
 * 初回呼び出し時にクライアントを初期化し、以降は同じインスタンスを返す。
 *
 * @returns LINE SDK クライアントインスタンス
 * @throws {Error} 環境変数 LINE_CHANNEL_ACCESS_TOKEN が未設定の場合
 */
export function getLineClient(): Client {
  if (lineClient === null) {
    const channelAccessToken = getLineChannelAccessToken();

    const config: ClientConfig = {
      channelAccessToken,
    };

    lineClient = new Client(config);
  }

  return lineClient;
}
