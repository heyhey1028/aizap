# -----------------------------------------------------------------------------
# Terraform Backend Configuration
# -----------------------------------------------------------------------------

terraform {
  backend "gcs" {
    bucket = "aizap-dev-backend"
    prefix = "terraform/state"
  }
}

