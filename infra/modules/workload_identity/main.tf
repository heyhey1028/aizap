# -----------------------------------------------------------------------------
# Workload Identity Federation
# GitHub Actions から GCP へ認証するための設定
# -----------------------------------------------------------------------------

resource "google_iam_workload_identity_pool" "this" {
  project                   = var.project_id
  workload_identity_pool_id = var.pool_id
  display_name              = var.pool_display_name
  description               = var.pool_description
}

resource "google_iam_workload_identity_pool_provider" "this" {
  project                            = var.project_id
  workload_identity_pool_id          = google_iam_workload_identity_pool.this.workload_identity_pool_id
  workload_identity_pool_provider_id = var.provider_id
  display_name                       = var.provider_display_name

  attribute_condition = var.attribute_condition
  attribute_mapping   = var.attribute_mapping

  oidc {
    issuer_uri = var.issuer_uri
  }
}

resource "google_service_account_iam_member" "workload_identity_user" {
  service_account_id = var.service_account_id
  role               = "roles/iam.workloadIdentityUser"
  member             = "principal://iam.googleapis.com/${google_iam_workload_identity_pool.this.name}/subject/${var.github_repository}"
}
