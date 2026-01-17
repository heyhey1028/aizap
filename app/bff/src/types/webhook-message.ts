// TODO: 画像や動画メッセージに対応する際に 'image' | 'video' 等を追加
export type MessageType = 'text';

/**
 * Pub/Sub 経由で BFF から Worker へ送信するメッセージ
 */
export interface WebhookMessage {
  /** LINE ユーザー ID */
  userId: string;
  /** 返信用トークン（Pub/Sub 経由では有効期限切れの可能性あり） */
  replyToken: string;
  /** メッセージ ID */
  messageId: string;
  /** メッセージタイプ */
  type: MessageType;
  /** テキストメッセージの内容 */
  text: string;
  /** Agent Engine のセッション ID（新規セッションの場合は undefined） */
  sessionId?: string;
  /** タイムスタンプ（ISO 8601 形式） */
  timestamp: string;
}

/**
 * WebhookMessage を Pub/Sub 用に Base64 エンコードする。
 *
 * @param message エンコードする WebhookMessage
 * @returns Base64 エンコードされた文字列
 */
export function encodeWebhookMessage(message: WebhookMessage): string {
  const json = JSON.stringify(message);
  return Buffer.from(json).toString('base64');
}
