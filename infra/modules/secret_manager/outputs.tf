# -----------------------------------------------------------------------------
# Secret Manager Module - Outputs
# -----------------------------------------------------------------------------

output "cloud_run_secrets" {
  description = "Cloud Run サービスで使用するシークレットの map（環境変数名をキー、シークレット名を値とする）"
  value = {
    LINE_CHANNEL_SECRET       = google_secret_manager_secret.line_channel_secret.name
    LINE_CHANNEL_ACCESS_TOKEN = google_secret_manager_secret.line_channel_access_token.name
  }
}
