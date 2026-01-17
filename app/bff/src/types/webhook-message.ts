export type MessageType = 'text' | 'image' | 'video' | 'audio';

/**
 * Pub/Sub 経由で BFF から Worker へ送信するメッセージ
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
 * WebhookMessage を Pub/Sub 用に Base64 エンコードする。
 *
 * @param message エンコードする WebhookMessage
 * @returns Base64 エンコードされた文字列
 */
export function encodeWebhookMessage(message: WebhookMessage): string {
  const json = JSON.stringify(message);
  return Buffer.from(json).toString('base64');
}
