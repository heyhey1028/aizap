# -----------------------------------------------------------------------------
# Cloud SQL Module - Variables
# -----------------------------------------------------------------------------

variable "project_id" {
  description = "GCP プロジェクト ID"
  type        = string
}

variable "region" {
  description = "Cloud SQL インスタンスのリージョン"
  type        = string
}

variable "instance_name" {
  description = "Cloud SQL インスタンス名"
  type        = string
}

variable "database_name" {
  description = "データベース名"
  type        = string
}

variable "availability_type" {
  description = "可用性タイプ（ZONAL または REGIONAL）"
  type        = string
}

variable "deletion_protection" {
  description = "削除保護"
  type        = bool
}

variable "retained_backups" {
  description = "バックアップ保持数"
  type        = number
}

variable "iam_users" {
  description = "IAM認証ユーザーのサービスアカウント ID リスト"
  type        = list(string)
}

variable "activation_policy" {
  description = "インスタンスのアクティベーションポリシー（ALWAYS: 起動, NEVER: 停止）"
  type        = string
}
