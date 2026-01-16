import { Hono } from 'hono';

const api: Hono = new Hono();

api.get('/hello', (c) => {
  return c.json({ status: 'hellow world!' });
});

export default api;
