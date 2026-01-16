import { Hono } from 'hono';
import type { WebhookRequestBody } from '@line/bot-sdk';
import { validateWebhookSignature } from '@/utils/signature.js';
import { processWebhookEvents } from '@/services/line/webhook.js';

const api: Hono = new Hono();

api.get('/hello', (c) => {
  return c.json({ status: 'hellow world!' });
});

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

    // パースしてイベントを処理
    const body = JSON.parse(rawBody) as WebhookRequestBody;
    await processWebhookEvents(body);
    console.log('Webhook received and processed successfully');
    return c.json({ status: 'ok' }, 200);
  } catch (error) {
    console.error('Webhook error:', error);
    return c.json({ error: 'Internal Server Error' }, 500);
  }
});

export default api;
