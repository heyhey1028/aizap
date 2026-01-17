import { PubSub } from '@google-cloud/pubsub';
import { logger } from '@/utils/logger.js';
import { getPubSubTopicName } from '@/config/env.js';
import type { WebhookMessage } from '@/types/index.js';
import { encodeWebhookMessage } from '@/types/index.js';

/**
 * Pub/Sub クライアントを取得する。
 * 初回呼び出し時にクライアントを初期化し、以降は同じインスタンスを返す。
 *
 * @returns Pub/Sub クライアントインスタンス
 */
export function getPubSubClient(): PubSub {
  return new PubSub();
}

/**
 * Webhook メッセージを Pub/Sub にパブリッシュする。
 *
 * @param message パブリッシュする WebhookMessage
 * @returns パブリッシュされたメッセージ ID
 */
export async function publishWebhookMessage(
  message: WebhookMessage
): Promise<string> {
  const client = getPubSubClient();
  const topicName = getPubSubTopicName();

  const data = encodeWebhookMessage(message);
  const dataBuffer = Buffer.from(data, 'base64');

  try {
    const messageId = await client.topic(topicName).publishMessage({
      data: dataBuffer,
      attributes: {
        userId: message.userId,
        messageType: message.type,
      },
    });

    logger.info({ messageId, userId: message.userId }, 'Published to Pub/Sub');
    return messageId;
  } catch (error) {
    logger.error({ err: error, userId: message.userId }, 'Failed to publish');
    throw error;
  }
}
