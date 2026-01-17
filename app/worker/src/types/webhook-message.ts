/**
 * Webhook メッセージ型定義
 *
 * BFF から Pub/Sub 経由で受信するメッセージのスキーマを定義する。
 */

// TODO: 画像や動画メッセージに対応する際に 'image' | 'video' 等を追加
/** メッセージタイプ */
export type MessageType = 'text';

/**
 * Pub/Sub 経由で BFF から Worker へ送信されるメッセージ
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
 * Pub/Sub Push メッセージのエンベロープ
 */
export interface PubSubPushMessage {
  message: {
    /** Base64 エンコードされたメッセージデータ */
    data: string;
    /** メッセージ ID */
    messageId: string;
    /** パブリッシュ時刻 */
    publishTime: string;
    /** メッセージ属性 */
    attributes?: Record<string, string>;
  };
  /** サブスクリプション名 */
  subscription: string;
}

/**
 * Pub/Sub メッセージデータを Base64 デコードして WebhookMessage に変換する。
 *
 * @param data Base64 エンコードされたメッセージデータ
 * @returns デコードされた WebhookMessage
 */
export function decodeWebhookMessage(data: string): WebhookMessage {
  const decoded = Buffer.from(data, 'base64').toString('utf-8');
  return JSON.parse(decoded) as WebhookMessage;
}
