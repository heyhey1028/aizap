import { Hono } from 'hono';
import type { WebhookRequestBody } from '@line/bot-sdk';
import { validateWebhookSignature } from '@/services/line/signature.js';
import { logger } from '@/utils/logger.js';
import { getLineClient } from '@/clients/line.js';

const api: Hono = new Hono();

api.post('/webhook', async (c) => {
  try {
    // 署名検証のため、生のボディを文字列として取得
    const rawBody = await c.req.text();
    const signature = c.req.header('X-Line-Signature');

    if (!signature) {
      return c.json({ error: 'Missing signature' }, 400);
    }

    // 署名検証を実行
    const isValid = validateWebhookSignature(rawBody, signature);
    if (!isValid) {
      return c.json({ error: 'Invalid signature' }, 400);
    }
    const body = JSON.parse(rawBody) as WebhookRequestBody;

    // eventsの配列が空の場合はLINEからのhealth checkのため早期リターン
    if (body.events.length === 0) {
      logger.info('Health check received');
      return c.json({ status: 'ok' }, 200);
    }

    // TODO:仮実装
    const client = getLineClient();
    await Promise.all(
      body.events.map((event) => {
        if (event.type !== 'message') {
          return;
        }
        if (event.message.type !== 'text') {
          return;
        }
        client.replyMessage(event.replyToken, {
          type: 'text',
          text: `reply: ${event.message.text}`,
        });
      })
    );

    logger.info('Webhook received and processed successfully');
    return c.json({ status: 'ok' }, 200);
  } catch (error) {
    logger.error({ err: error }, 'Webhook error');
    return c.json({ error: 'Internal Server Error' }, 500);
  }
});

export default api;
