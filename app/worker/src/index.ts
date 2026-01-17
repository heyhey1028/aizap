/**
 * aizap-worker エントリポイント
 *
 * Pub/Sub Push を受信し、Agent Engine を呼び出して LINE に返信する。
 */
import { serve } from '@hono/node-server';
import { Hono } from 'hono';
import api from '@/apis/webhook.js';
import { logger } from '@/utils/logger.js';
import { accessLog } from '@/middleware/accessLog.js';

export const app = new Hono();
const port = Number(process.env.PORT) || 8080;

app.use(accessLog);
app.get('/health', (c) => {
  return c.json({ status: 'ok' });
});
app.notFound((c) => c.json({ message: 'Not Found' }, 404));

app.route('/', api);

const server = serve({
  fetch: app.fetch,
  port,
});

// graceful shutdown
process.on('SIGINT', () => {
  server.close((err) => {
    if (err) {
      logger.error({ err }, 'Error during graceful shutdown');
      process.exit(1);
    }
  });
  process.exit(0);
});
process.on('SIGTERM', () => {
  server.close((err) => {
    if (err) {
      logger.error({ err }, 'Error during graceful shutdown');
      process.exit(1);
    }
    process.exit(0);
  });
});

logger.info({ port }, 'Server is running');

export default app;
