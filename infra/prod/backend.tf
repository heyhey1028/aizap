# -----------------------------------------------------------------------------
# Terraform Backend Configuration
# -----------------------------------------------------------------------------

terraform {
  backend "gcs" {
    bucket = "aizap-prod-backend"
    prefix = "terraform/state"
  }
}

