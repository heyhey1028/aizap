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
# Data Sources
# -----------------------------------------------------------------------------

data "google_project" "project" {
  project_id = var.project_id
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
    "telemetry.googleapis.com",
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
    "roles/serviceusage.serviceUsageConsumer",
  ]

  depends_on = [google_project_service.apis]
}

# 開発者がローカルから ADK サービスアカウントを偽装できるようにする
# gcloud auth application-default login --impersonate-service-account=aizap-adk-sa@PROJECT.iam.gserviceaccount.com
# 注意: allAuthenticatedUsers は GCP にログインしている全ユーザーが偽装可能
resource "google_service_account_iam_member" "adk_agent_token_creator" {
  service_account_id = module.sa_adk_agent.id
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "allAuthenticatedUsers"

  depends_on = [module.sa_adk_agent]
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
# Cloud Storage (LINE Media)
# -----------------------------------------------------------------------------

resource "google_storage_bucket" "line_media" {
  project                     = var.project_id
  name                        = "${var.project_id}-line-media"
  location                    = var.region
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  depends_on = [google_project_service.apis]
}

resource "google_storage_bucket_iam_member" "line_media_worker" {
  bucket = google_storage_bucket.line_media.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${module.sa_worker.email}"

  depends_on = [google_project_service.apis, module.sa_worker, google_storage_bucket.line_media]
}

resource "google_storage_bucket_iam_member" "line_media_adk_viewer" {
  bucket = google_storage_bucket.line_media.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${module.sa_adk_agent.email}"

  depends_on = [google_project_service.apis, module.sa_adk_agent, google_storage_bucket.line_media]
}

# Vertex AI Service Agent が GCS からメディアを読み取るための権限
# Gemini が file_data で GCS URI を読み取る際に使用される
resource "google_storage_bucket_iam_member" "line_media_vertex_ai" {
  bucket = google_storage_bucket.line_media.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-aiplatform.iam.gserviceaccount.com"

  depends_on = [google_project_service.apis, google_storage_bucket.line_media]
}

# Vertex AI Service Agent に serviceusage.serviceUsageConsumer を付与
# Agent Engine 内部の OpenTelemetry スパンエクスポートに必要
resource "google_project_iam_member" "vertex_ai_service_usage" {
  project = var.project_id
  role    = "roles/serviceusage.serviceUsageConsumer"
  member  = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-aiplatform.iam.gserviceaccount.com"

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
  activation_policy   = "ALWAYS"
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
    GCS_MEDIA_BUCKET_NAME    = google_storage_bucket.line_media.name
  }
  secrets                   = module.aizap_secrets.cloud_run_secrets
  min_instance_count        = 0
  max_instance_count        = 5
  allow_unauthenticated     = false
  cloud_sql_connection_name = module.cloud_sql.connection_name
  health_check_path         = "/health"

  depends_on = [google_project_service.apis, module.sa_worker, module.cloud_sql, module.aizap_secrets]
}

# Pub/Sub Push から Worker を呼び出すための権限
resource "google_cloud_run_v2_service_iam_member" "worker_invoker_pubsub" {
  project  = var.project_id
  location = var.region
  name     = module.cloud_run_worker.service_name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${module.sa_worker.email}"

  depends_on = [module.cloud_run_worker]
}

# -----------------------------------------------------------------------------
# Cloud Run Jobs (Prisma Migration)
# -----------------------------------------------------------------------------

resource "google_cloud_run_v2_job" "db_migrate" {
  name     = "aizap-db-migrate"
  location = var.region

  template {
    template {
      service_account = module.sa_worker.email

      containers {
        name    = "migrate"
        image   = var.image_worker
        command = ["pnpm"]
        args    = ["prisma", "migrate", "deploy"]
        env {
          name  = "DATABASE_URL"
          value = "postgresql://${module.sa_worker.account_id}@${var.project_id}.iam@localhost:5432/${module.cloud_sql.database_name}"
        }
        depends_on = ["cloud-sql-proxy"]
      }

      containers {
        name  = "cloud-sql-proxy"
        image = "gcr.io/cloud-sql-connectors/cloud-sql-proxy:2.20.0"
        args = [
          "--address=0.0.0.0",
          "--port=5432",
          "--auto-iam-authn",
          module.cloud_sql.connection_name,
        ]
        startup_probe {
          tcp_socket {
            port = 5432
          }
          initial_delay_seconds = 0
          period_seconds        = 1
          timeout_seconds       = 1
          failure_threshold     = 60
        }
      }
    }
  }

  depends_on = [
    google_project_service.apis,
    module.sa_worker,
    module.cloud_sql,
  ]
}

# -----------------------------------------------------------------------------
# Pub/Sub
# -----------------------------------------------------------------------------

module "pubsub_webhook" {
  source = "../modules/pubsub"

  project_id                 = var.project_id
  project_number             = data.google_project.project.number
  topic_name                 = "aizap-webhook-events"
  subscription_name          = "aizap-webhook-events-sub"
  push_endpoint              = "${module.cloud_run_worker.service_uri}/webhook"
  push_audience              = module.cloud_run_worker.service_uri
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

