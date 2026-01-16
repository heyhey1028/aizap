import { Hono } from 'hono';
import type { WebhookRequestBody } from '@line/bot-sdk';

const api: Hono = new Hono();

api.get('/hello', (c) => {
  return c.json({ status: 'hellow world!' });
});

api.post('/webhook', async (c) => {
  try {
    const body = await c.req.json<WebhookRequestBody>();

    console.log('Received webhook:', JSON.stringify(body, null, 2));
    return c.json({ status: 'ok' }, 200);
  } catch (error) {
    console.error('Webhook error:', error);
    return c.json({ error: 'Internal Server Error' }, 500);
  }
});

export default api;
