# -----------------------------------------------------------------------------
# Terraform Configuration for prod environment
# -----------------------------------------------------------------------------

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.15"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# -----------------------------------------------------------------------------
# Local Variables
# -----------------------------------------------------------------------------

locals {
  services = [
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
    "cloudbuild.googleapis.com",
    "aiplatform.googleapis.com",
    "pubsub.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "secretmanager.googleapis.com",
    "sqladmin.googleapis.com",
  ]
}

# -----------------------------------------------------------------------------
# Enable APIs
# -----------------------------------------------------------------------------

resource "google_project_service" "apis" {
  for_each = toset(local.services)

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

# -----------------------------------------------------------------------------
# Service Accounts
# -----------------------------------------------------------------------------

module "sa_bff" {
  source = "../modules/service_account"

  project_id   = var.project_id
  account_id   = "aizap-bff-sa"
  display_name = "aizap-bff-sa"
  description  = "BFF (Webhook/LIFF)"
  roles = [
    "roles/pubsub.publisher",
    "roles/secretmanager.secretAccessor",
  ]

  depends_on = [google_project_service.apis]
}

module "sa_worker" {
  source = "../modules/service_account"

  project_id   = var.project_id
  account_id   = "aizap-worker-sa"
  display_name = "aizap-worker-sa"
  description  = "Worker (Pub/Sub Push -> Agent Engine -> LINE)"
  roles = [
    "roles/pubsub.subscriber",
    "roles/cloudsql.client",
    "roles/cloudsql.instanceUser",
    "roles/aiplatform.user",
    "roles/secretmanager.secretAccessor",
  ]

  depends_on = [google_project_service.apis]
}

module "sa_github_actions" {
  source = "../modules/service_account"

  project_id   = var.project_id
  account_id   = "github-actions-sa"
  display_name = "github-actions-sa"
  description  = "GitHub Actions -> GCP"
  roles = [
    "roles/artifactregistry.admin",
    "roles/cloudbuild.builds.builder",
    "roles/logging.viewer",
    "roles/run.admin",
    "roles/pubsub.admin",
    "roles/iam.serviceAccountAdmin",
    "roles/iam.serviceAccountUser",
    "roles/iam.workloadIdentityPoolAdmin",
    "roles/resourcemanager.projectIamAdmin",
    "roles/serviceusage.serviceUsageAdmin",
    "roles/storage.admin",
    "roles/aiplatform.admin",
    "roles/secretmanager.admin",
    "roles/cloudsql.admin",
  ]

  depends_on = [google_project_service.apis]
}

module "sa_adk_agent" {
  source = "../modules/service_account"

  project_id   = var.project_id
  account_id   = "aizap-adk-sa"
  display_name = "aizap-adk-sa"
  description  = "ADK Agent running on Agent Engine"
  roles = [
    "roles/aiplatform.user",
    "roles/cloudsql.client",
    "roles/cloudsql.instanceUser",
  ]

  depends_on = [google_project_service.apis]
}

# -----------------------------------------------------------------------------
# Cloud Storage (Agent Engine Staging)
# -----------------------------------------------------------------------------

resource "google_storage_bucket" "staging" {
  project                     = var.project_id
  name                        = "${var.project_id}-staging"
  location                    = var.region
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }

  depends_on = [google_project_service.apis]
}

# -----------------------------------------------------------------------------
# Artifact Registry
# -----------------------------------------------------------------------------

resource "google_artifact_registry_repository" "images" {
  project       = var.project_id
  location      = var.region
  repository_id = "aizap-images"
  description   = "aizap 用コンテナイメージ"
  format        = "DOCKER"

  depends_on = [google_project_service.apis]
}

# -----------------------------------------------------------------------------
# Secret Manager
# -----------------------------------------------------------------------------

module "aizap_secrets" {
  source = "../modules/secret_manager"

  project_id = var.project_id

  depends_on = [google_project_service.apis]
}

# -----------------------------------------------------------------------------
# Cloud SQL (PostgreSQL)
# -----------------------------------------------------------------------------

module "cloud_sql" {
  source = "../modules/cloud_sql"

  project_id        = var.project_id
  region            = var.region
  instance_name     = "aizap-postgres-prod"
  database_name     = "aizap"
  availability_type = "REGIONAL"
  # 本番でテストする際は "ALWAYS" に変更すること
  # 現在は過剰な課金を抑えるためインスタンスを停止中
  activation_policy   = "NEVER"
  deletion_protection = true
  retained_backups    = 30
  iam_users = [
    module.sa_worker.account_id,
    module.sa_adk_agent.account_id,
  ]

  depends_on = [google_project_service.apis, module.sa_worker, module.sa_adk_agent]
}

# -----------------------------------------------------------------------------
# Cloud Run Services
# -----------------------------------------------------------------------------

module "cloud_run_bff" {
  source = "../modules/cloud_run"

  project_id            = var.project_id
  location              = var.region
  name                  = "aizap-bff"
  image                 = var.image_bff
  service_account_email = module.sa_bff.email
  env_vars = {
    ENVIRONMENT       = var.environment
    PUBSUB_TOPIC_NAME = "aizap-webhook-events"
  }
  secrets                   = module.aizap_secrets.cloud_run_secrets
  min_instance_count        = 0
  max_instance_count        = 5
  allow_unauthenticated     = true
  cloud_sql_connection_name = null
  health_check_path         = "/healthz"

  depends_on = [
    google_project_service.apis,
    module.sa_bff,
    module.aizap_secrets,
  ]
}

module "cloud_run_worker" {
  source = "../modules/cloud_run"

  project_id            = var.project_id
  location              = var.region
  name                  = "aizap-worker"
  image                 = var.image_worker
  service_account_email = module.sa_worker.email
  env_vars = {
    ENVIRONMENT              = var.environment
    DATABASE_URL             = "postgresql://${module.sa_worker.account_id}@${var.project_id}.iam@localhost:5432/${module.cloud_sql.database_name}"
    GCP_PROJECT_ID           = var.project_id
    GCP_REGION               = var.region
    AGENT_ENGINE_RESOURCE_ID = var.agent_engine_resource_id
  }
  secrets                   = module.aizap_secrets.cloud_run_secrets
  min_instance_count        = 0
  max_instance_count        = 5
  allow_unauthenticated     = false
  cloud_sql_connection_name = module.cloud_sql.connection_name
  health_check_path         = "/health"

  depends_on = [google_project_service.apis, module.sa_worker, module.cloud_sql, module.aizap_secrets]
}

# -----------------------------------------------------------------------------
# Pub/Sub
# -----------------------------------------------------------------------------

module "pubsub_webhook" {
  source = "../modules/pubsub"

  project_id                 = var.project_id
  topic_name                 = "aizap-webhook-events"
  subscription_name          = "aizap-webhook-events-sub"
  push_endpoint              = "${module.cloud_run_worker.service_uri}/webhook"
  push_service_account_email = module.sa_worker.email
  ack_deadline_seconds       = 60
  message_retention_duration = "604800s"

  depends_on = [
    google_project_service.apis,
    module.cloud_run_worker,
    module.sa_worker,
  ]
}

# -----------------------------------------------------------------------------
# Workload Identity Federation
# -----------------------------------------------------------------------------

module "workload_identity" {
  source = "../modules/workload_identity"

  project_id            = var.project_id
  pool_id               = "github-actions-pool"
  pool_display_name     = "github-actions-pool"
  pool_description      = "GitHub Actions 用 Workload Identity Pool"
  provider_id           = "github-actions-provider"
  provider_display_name = "github-actions-provider"
  attribute_condition   = "assertion.repository_owner == \"heyhey1028\""
  attribute_mapping = {
    "google.subject" = "assertion.repository"
  }
  issuer_uri         = "https://token.actions.githubusercontent.com"
  service_account_id = module.sa_github_actions.id
  github_repository  = "heyhey1028/aizap"

  depends_on = [google_project_service.apis, module.sa_github_actions]
}

