// middleware/accessLog.ts
import type { MiddlewareHandler } from 'hono';
import { logger } from '@/utils/logger.js';

export const accessLog: MiddlewareHandler = async (c, next) => {
  const start = Date.now();

  try {
    await next();
  } finally {
    logger.info({
      type: 'access',
      method: c.req.method,
      path: new URL(c.req.url).pathname,
      status: c.res.status,
      latencyMs: Date.now() - start,
    });
  }
};
