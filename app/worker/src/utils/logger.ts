/**
 * ロガー
 *
 * pino を使用した構造化ログ出力。
 * ログレベルは環境変数 LOG_LEVEL で設定可能（デフォルト: info）。
 */
import pino from 'pino';

/**
 * ログレベルを取得する。
 *
 * @returns ログレベル
 */
function getLogLevel(): string {
  return process.env.LOG_LEVEL || 'info';
}

/** 共通ロガーインスタンス */
export const logger = pino({
  level: getLogLevel(),
});
