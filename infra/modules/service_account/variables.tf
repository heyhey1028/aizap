# -----------------------------------------------------------------------------
# Variables
# -----------------------------------------------------------------------------

variable "project_id" {
  description = "GCP プロジェクト ID"
  type        = string
}

variable "account_id" {
  description = "サービスアカウントのアカウント ID（6-30文字、小文字・数字・ハイフンのみ）"
  type        = string
}

variable "display_name" {
  description = "サービスアカウントの表示名"
  type        = string
}

variable "description" {
  description = "サービスアカウントの説明"
  type        = string
}

variable "roles" {
  description = "サービスアカウントに付与する IAM ロールのリスト（プロジェクトレベル）"
  type        = list(string)
}
