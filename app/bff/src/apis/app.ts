import { Hono } from 'hono';
const api = new Hono();

api.get('/hello', (c) => {
  return c.json({ status: 'hellow world!' });
});

export default api;
