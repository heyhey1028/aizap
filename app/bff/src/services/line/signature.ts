import { validateSignature } from '@line/bot-sdk';
import { getLineChannelSecret } from '@/config/env.js';

/**
 * LINE Webhook の署名を検証する。
 *
 * @param body - リクエストボディ（生の文字列または Buffer）
 * @param signature - X-Line-Signature ヘッダーの値
 * @returns 署名が有効な場合 true、無効な場合 false
 * @throws {Error} 環境変数 LINE_CHANNEL_SECRET が未設定の場合
 */
export function validateWebhookSignature(
  body: string | Buffer,
  signature: string
): boolean {
  const channelSecret = getLineChannelSecret();

  return validateSignature(body, channelSecret, signature);
}
