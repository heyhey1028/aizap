/**
 * Webhook メッセージ型定義
 *
 * BFF から Pub/Sub 経由で受信するメッセージのスキーマを定義する。
 */

/** メッセージタイプ */
export type MessageType = 'text' | 'image' | 'video' | 'audio';

/**
 * Pub/Sub 経由で BFF から Worker へ送信されるメッセージ
 */
interface WebhookMessageBase {
  /** LINE ユーザー ID */
  userId: string;
  /** 返信用トークン（Pub/Sub 経由では有効期限切れの可能性あり） */
  replyToken: string;
  /** メッセージ ID */
  messageId: string;
  /** メッセージタイプ */
  type: MessageType;
  /** Agent Engine のセッション ID（新規セッションの場合は undefined） */
  sessionId?: string;
  /** タイムスタンプ（ISO 8601 形式） */
  timestamp: string;
}

export type WebhookMessage =
  | (WebhookMessageBase & {
      /** テキストメッセージの内容 */
      type: 'text';
      text: string;
    })
  | (WebhookMessageBase & {
      type: 'image';
    })
  | (WebhookMessageBase & {
      type: 'video';
    })
  | (WebhookMessageBase & {
      type: 'audio';
    });

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
