import { Hono } from 'hono';
import type { WebhookEvent } from '@line/bot-sdk';
import { logger } from '@/utils/logger.js';
import { getLineClient } from '@/clients/line.js';
import { lineMiddleware } from '@/middleware/line.js';
import { getLineChannelSecret } from '@/config/env.js';

const api: Hono = new Hono();
const client = getLineClient();

const handleEvent = async (event: WebhookEvent) => {
  if (event.type !== 'message' || event.message.type !== 'text') return;

  await client.replyMessage({
    replyToken: event.replyToken,
    messages: [
      {
        type: 'text',
        text: `reply: ${event.message.text}`,
      },
    ],
  });
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
