# -----------------------------------------------------------------------------
# Pub/Sub Module - Variables
# -----------------------------------------------------------------------------

variable "project_id" {
  description = "GCP プロジェクト ID"
  type        = string
}

variable "topic_name" {
  description = "Pub/Sub トピック名"
  type        = string
}

variable "subscription_name" {
  description = "Pub/Sub サブスクリプション名"
  type        = string
}

variable "push_endpoint" {
  description = "Push 先のエンドポイント URL"
  type        = string
}

variable "push_service_account_email" {
  description = "Push 時の OIDC 認証に使用するサービスアカウントのメールアドレス"
  type        = string
}

variable "push_audience" {
  description = "OIDC トークンの audience（Cloud Run のサービス URL）"
  type        = string
  default     = null
}

variable "ack_deadline_seconds" {
  description = "確認応答のデッドライン（秒）"
  type        = number
}

variable "message_retention_duration" {
  description = "メッセージの保持期間（例: 604800s = 7日間）"
  type        = string
}

