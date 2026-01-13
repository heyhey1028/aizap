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
