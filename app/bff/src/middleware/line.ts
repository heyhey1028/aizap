import { createMiddleware } from 'hono/factory';
import type { WebhookRequestBody } from '@line/bot-sdk';
import { validateSignature } from '@line/bot-sdk';

declare module 'hono' {
  interface ContextVariableMap {
    body: WebhookRequestBody;
  }
}

export const lineMiddleware = (config: { channelSecret: string }) => {
  return createMiddleware(async (c, next) => {
    const signature = c.req.header('X-Line-Signature');
    if (!signature) {
      return c.json({ error: 'Missing signature' }, 400);
    }

    const rawBody = await c.req.text();
    const isValid = validateSignature(rawBody, config.channelSecret, signature);
    if (!isValid) {
      return c.json({ error: 'Invalid signature' }, 400);
    }
    c.set('body', JSON.parse(rawBody));

    await next();
  });
};
