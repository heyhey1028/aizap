# -----------------------------------------------------------------------------
# Pub/Sub Module
# Reference: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/pubsub_topic
# Reference: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/pubsub_subscription
# -----------------------------------------------------------------------------

resource "google_pubsub_topic" "this" {
  project = var.project_id
  name    = var.topic_name

  message_retention_duration = var.message_retention_duration
}

resource "google_pubsub_subscription" "this" {
  project = var.project_id
  name    = var.subscription_name
  topic   = google_pubsub_topic.this.id

  ack_deadline_seconds       = var.ack_deadline_seconds
  message_retention_duration = var.message_retention_duration

  push_config {
    push_endpoint = var.push_endpoint

    oidc_token {
      service_account_email = var.push_service_account_email
    }

    attributes = {
      x-goog-version = "v1"
    }
  }

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }
}

# Pub/Sub が OIDC トークンを発行できるようにする
data "google_project" "this" {
  project_id = var.project_id
}

resource "google_service_account_iam_member" "pubsub_token_creator" {
  service_account_id = "projects/${var.project_id}/serviceAccounts/${var.push_service_account_email}"
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "serviceAccount:service-${data.google_project.this.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
}

