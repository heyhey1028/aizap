import { Hono } from 'hono';
import type { WebhookEvent } from '@line/bot-sdk';
import { logger } from '@/utils/logger.js';
import { lineMiddleware } from '@/middleware/line.js';
import { getLineChannelSecret } from '@/config/env.js';
import { publishWebhookMessage } from '@/clients/pubsub.js';
import type { WebhookMessage } from '@/types/index.js';

const api: Hono = new Hono();

// TODO: 画像や動画メッセージにも対応する（GCSアップロード等）
const handleEvent = async (event: WebhookEvent) => {
  if (event.type !== 'message' || event.message.type !== 'text') return;

  const userId = event.source.userId;
  if (!userId) return;

  const message: WebhookMessage = {
    userId,
    replyToken: event.replyToken,
    messageId: event.message.id,
    type: 'text',
    text: event.message.text,
    timestamp: new Date(event.timestamp).toISOString(),
  };

  await publishWebhookMessage(message);
};

api.post(
  '/webhook',
  lineMiddleware({ channelSecret: getLineChannelSecret() }),
  async (c) => {
    try {
      const { events } = c.get('body');
      // eventsの配列が空の場合はLINEからのhealth checkのため早期リターン
      if (events.length === 0) {
        logger.info('Health check received');
        return c.json({ status: 'ok' }, 200);
      }

      await Promise.all(events.map(handleEvent));

      logger.info('Webhook received and processed successfully');
      return c.json({ status: 'success' }, 200);
    } catch (error) {
      logger.error({ err: error }, 'Webhook error');
      return c.json({ error: 'Internal Server Error' }, 500);
    }
  }
);

export default api;
