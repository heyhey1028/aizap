# -----------------------------------------------------------------------------
# Service Account Module
# Reference: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/google_service_account
# -----------------------------------------------------------------------------

resource "google_service_account" "this" {
  project      = var.project_id
  account_id   = var.account_id
  display_name = var.display_name
  description  = var.description
}

# -----------------------------------------------------------------------------
# IAM Bindings (Project Level)
# Reference: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/google_project_iam
# -----------------------------------------------------------------------------

resource "google_project_iam_member" "roles" {
  for_each = toset(var.roles)

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.this.email}"
}
