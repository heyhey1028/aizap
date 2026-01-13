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

