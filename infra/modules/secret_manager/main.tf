# -----------------------------------------------------------------------------
# Secret Manager Module (LINE Secrets)
# Reference: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/secret_manager_secret
# Note: シークレットの値は gcloud CLI で手動で追加してください
# -----------------------------------------------------------------------------

resource "google_secret_manager_secret" "line_channel_secret" {
  project   = var.project_id
  secret_id = "LINE_CHANNEL_SECRET"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "line_channel_access_token" {
  project   = var.project_id
  secret_id = "LINE_CHANNEL_ACCESS_TOKEN"

  replication {
    auto {}
  }
}
