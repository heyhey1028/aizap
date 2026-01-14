import { serve } from '@hono/node-server';
import { Hono } from 'hono';
import api from '@/apis/app';
import web from '@/pages/app';

export const app = new Hono();
const port = Number(process.env.PORT) || 8081;

app.get('/healthz', (c) => {
  return c.json({ status: 'ok' });
});
app.notFound((c) => c.json({ message: 'Not Found' }, 404));

app.route('/api', api);
app.route('/web', web);

serve({
  fetch: app.fetch,
  port,
});

console.log(`Server is running on port ${port}`);

export default app;
