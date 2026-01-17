/**
 * アクセスログミドルウェア
 *
 * HTTP リクエストのメソッド、パス、ステータス、レイテンシをログ出力する。
 */
import type { MiddlewareHandler } from 'hono';
import { logger } from '@/utils/logger.js';

/**
 * アクセスログを出力するミドルウェア
 */
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
