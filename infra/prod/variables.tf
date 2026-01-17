# -----------------------------------------------------------------------------
# Variables（GitHub Actions から -var= で渡される）
# -----------------------------------------------------------------------------

variable "project_id" {
  description = "GCP プロジェクト ID"
  type        = string
}

variable "region" {
  description = "GCP リージョン"
  type        = string
}

variable "environment" {
  description = "環境名（dev / prod）"
  type        = string
}

variable "image_bff" {
  description = "aizap-bff のコンテナイメージ URI"
  type        = string
}

variable "image_worker" {
  description = "aizap-worker のコンテナイメージ URI"
  type        = string
}

variable "agent_engine_resource_id" {
  description = "Agent Engine のリソース ID（Reasoning Engine ID）"
  type        = string
}
