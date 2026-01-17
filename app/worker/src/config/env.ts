/**
 * 環境変数管理
 *
 * Worker が必要とする環境変数を取得する。
 * 必須の環境変数が未設定の場合はエラーをスローする。
 */

/**
 * GCP プロジェクト ID を取得する。
 *
 * @returns GCP プロジェクト ID
 * @throws {Error} 環境変数 GCP_PROJECT_ID が未設定の場合
 */
export function getProjectId(): string {
  const value = process.env.GCP_PROJECT_ID;
  if (!value) {
    throw new Error('GCP_PROJECT_ID environment variable is not set');
  }
  return value;
}

/**
 * GCP リージョンを取得する。
 *
 * @returns GCP リージョン
 * @throws {Error} 環境変数 GCP_REGION が未設定の場合
 */
export function getRegion(): string {
  const value = process.env.GCP_REGION;
  if (!value) {
    throw new Error('GCP_REGION environment variable is not set');
  }
  return value;
}

/**
 * Agent Engine リソース ID を取得する。
 *
 * @returns Agent Engine リソース ID
 * @throws {Error} 環境変数 AGENT_ENGINE_RESOURCE_ID が未設定の場合
 */
export function getAgentEngineResourceId(): string {
  const value = process.env.AGENT_ENGINE_RESOURCE_ID;
  if (!value) {
    throw new Error('AGENT_ENGINE_RESOURCE_ID environment variable is not set');
  }
  return value;
}

/**
 * 画像/動画保存用の GCS バケット名を取得する。
 *
 * @returns GCS バケット名
 * @throws {Error} 環境変数 GCS_MEDIA_BUCKET_NAME が未設定の場合
 */
export function getMediaBucketName(): string {
  const value = process.env.GCS_MEDIA_BUCKET_NAME;
  if (!value) {
    throw new Error('GCS_MEDIA_BUCKET_NAME environment variable is not set');
  }
  return value;
}

/**
 * LINE チャネルアクセストークンを取得する。
 *
 * @returns LINE チャネルアクセストークン
 * @throws {Error} 環境変数 LINE_CHANNEL_ACCESS_TOKEN が未設定の場合
 */
export function getLineChannelAccessToken(): string {
  const value = process.env.LINE_CHANNEL_ACCESS_TOKEN;
  if (!value) {
    throw new Error('LINE_CHANNEL_ACCESS_TOKEN environment variable is not set');
  }
  return value;
}
