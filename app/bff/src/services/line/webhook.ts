import type {
  WebhookRequestBody,
  MessageEvent,
  TextEventMessage,
} from '@line/bot-sdk';
import { echoTextMessage } from './messaging.js';

/**
 * テキストメッセージイベントかどうかを判定する型ガード。
 *
 * @param event - イベント
 * @returns テキストメッセージイベントの場合 true
 */
function isTextMessageEvent(
  event: MessageEvent
): event is MessageEvent & { message: TextEventMessage } {
  return event.message.type === 'text';
}

/**
 * Webhook イベントを処理する。
 * テキストメッセージイベントを抽出し、オウム返しを実行する。
 *
 * @param body - Webhook リクエストボディ
 */
export async function processWebhookEvents(
  body: WebhookRequestBody
): Promise<void> {
  const { events } = body;

  // テキストメッセージイベントを抽出
  const textMessageEvents = events
    .filter((event): event is MessageEvent => event.type === 'message')
    .filter(isTextMessageEvent);

  // 各テキストメッセージに対してオウム返しを実行
  await Promise.all(
    textMessageEvents.map((event) =>
      echoTextMessage(event.replyToken, event.message.text)
    )
  );
}
