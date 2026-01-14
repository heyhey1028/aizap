import { serve } from '@hono/node-server';
import { Hono } from 'hono';

export const app = new Hono();
const port = Number(process.env.PORT) || 8080;

app.get('/', (c) => {
  return c.text('Hello, World!');
});

app.get('/health', (c) => {
  return c.json({ status: 'ok' });
});

app.post('/webhook', (c) => {
  // TODO: LINE 署名検証
  // TODO: Pub/Sub に Publish
  return c.text('', 200);
});

// テスト時はサーバーを起動しない
if (process.env.NODE_ENV !== 'test' && !process.env.VITEST) {
  serve({
    fetch: app.fetch,
    port,
  });

  console.log(`Server is running on port ${port}`);
}
