import pino from 'pino';

/**
 * ログレベルを取得する。
 * 環境変数 LOG_LEVEL から取得し、未設定の場合は 'info' を返す。
 *
 * @returns ログレベル
 */
function getLogLevel(): string {
  return process.env.LOG_LEVEL || 'info';
}

/**
 * pino logger
 */
export const logger = pino({
  level: getLogLevel(),
});
