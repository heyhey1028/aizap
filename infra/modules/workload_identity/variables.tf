# -----------------------------------------------------------------------------
# Variables
# -----------------------------------------------------------------------------

variable "project_id" {
  description = "GCP プロジェクト ID"
  type        = string
}

variable "pool_id" {
  description = "Workload Identity Pool の ID"
  type        = string
}

variable "pool_display_name" {
  description = "Workload Identity Pool の表示名"
  type        = string
}

variable "pool_description" {
  description = "Workload Identity Pool の説明"
  type        = string
}

variable "provider_id" {
  description = "Workload Identity Provider の ID"
  type        = string
}

variable "provider_display_name" {
  description = "Workload Identity Provider の表示名"
  type        = string
}

variable "attribute_condition" {
  description = "トークンの属性条件（例: assertion.repository_owner == \"org-name\"）"
  type        = string
}

variable "attribute_mapping" {
  description = "属性マッピング"
  type        = map(string)
}

variable "issuer_uri" {
  description = "OIDC Issuer URI"
  type        = string
}

variable "service_account_id" {
  description = "Workload Identity User ロールを付与する Service Account の ID"
  type        = string
}

variable "github_repository" {
  description = "GitHub リポジトリ（owner/repo 形式）"
  type        = string
}
