# -----------------------------------------------------------------------------
# Cloud Run Service Module - Variables
# -----------------------------------------------------------------------------

variable "project_id" {
  description = "GCP プロジェクト ID"
  type        = string
}

variable "location" {
  description = "Cloud Run のロケーション"
  type        = string
}

variable "name" {
  description = "Cloud Run サービス名"
  type        = string
}

variable "image" {
  description = "コンテナイメージの URL"
  type        = string
}

variable "service_account_email" {
  description = "Cloud Run サービスに紐づけるサービスアカウントのメールアドレス"
  type        = string
}

variable "env_vars" {
  description = "コンテナに設定する環境変数"
  type        = map(string)
}

variable "min_instance_count" {
  description = "最小インスタンス数"
  type        = number
}

variable "max_instance_count" {
  description = "最大インスタンス数"
  type        = number
}

variable "allow_unauthenticated" {
  description = "未認証アクセスを許可するかどうか"
  type        = bool
}

variable "secrets" {
  description = "環境変数名をキー、シークレット名を値とする map（例: { LINE_CHANNEL_SECRET = \"LINE_CHANNEL_SECRET\" }）"
  type        = map(string)
}

variable "cloud_sql_connection_name" {
  description = "Cloud SQL インスタンスの接続名（例: project:region:instance）。null の場合は Cloud SQL Proxy を無効化"
  type        = string
}

variable "health_check_path" {
  description = "Health check のパス（例: \"/healthz\"）。null の場合は health check を無効化"
  type        = string
}
