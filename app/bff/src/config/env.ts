/**
 * LINE チャネルアクセストークンを取得する。
 *
 * @returns LINE チャネルアクセストークン
 * @throws {Error} 環境変数 LINE_CHANNEL_ACCESS_TOKEN が未設定の場合
 */
export function getLineChannelAccessToken(): string {
  const value = process.env.LINE_CHANNEL_ACCESS_TOKEN;
  if (!value) {
    throw new Error(
      'LINE_CHANNEL_ACCESS_TOKEN environment variable is not set'
    );
  }
  return value;
}

/**
 * LINE チャネルシークレットを取得する。
 *
 * @returns LINE チャネルシークレット
 * @throws {Error} 環境変数 LINE_CHANNEL_SECRET が未設定の場合
 */
export function getLineChannelSecret(): string {
  const value = process.env.LINE_CHANNEL_SECRET;
  if (!value) {
    throw new Error('LINE_CHANNEL_SECRET environment variable is not set');
  }
  return value;
}
