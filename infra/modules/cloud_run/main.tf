# -----------------------------------------------------------------------------
# Cloud Run Service Module
# Reference: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloud_run_v2_service
# -----------------------------------------------------------------------------

resource "google_cloud_run_v2_service" "this" {
  name                = var.name
  location            = var.location
  project             = var.project_id
  deletion_protection = false
  ingress             = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = var.service_account_email

    scaling {
      min_instance_count = var.min_instance_count
      max_instance_count = var.max_instance_count
    }

    containers {
      name  = "app"
      image = var.image

      # Cloud SQL を使う場合、Proxy の起動を待つ
      depends_on = var.cloud_sql_connection_name != null && var.cloud_sql_connection_name != "" ? ["cloud-sql-proxy"] : []

      dynamic "env" {
        for_each = var.env_vars
        content {
          name  = env.key
          value = env.value
        }
      }

      dynamic "env" {
        for_each = var.secrets
        content {
          name = env.key
          value_source {
            secret_key_ref {
              secret  = env.value
              version = "latest"
            }
          }
        }
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }

      dynamic "startup_probe" {
        for_each = var.health_check_path != null ? [1] : []
        content {
          initial_delay_seconds = 0
          period_seconds        = 3
          timeout_seconds       = 1
          failure_threshold     = 3

          http_get {
            path = var.health_check_path
            port = 8080
          }
        }
      }

      dynamic "liveness_probe" {
        for_each = var.health_check_path != null ? [1] : []
        content {
          initial_delay_seconds = 0
          period_seconds        = 10
          timeout_seconds       = 1
          failure_threshold     = 3

          http_get {
            path = var.health_check_path
            port = 8080
          }
        }
      }
    }

    # Cloud SQL Auth Proxy sidecar（Cloud SQL を使う場合のみ -> worker service が対象）
    dynamic "containers" {
      for_each = var.cloud_sql_connection_name != null && var.cloud_sql_connection_name != "" ? [var.cloud_sql_connection_name] : []
      content {
        name  = "cloud-sql-proxy"
        image = "gcr.io/cloud-sql-connectors/cloud-sql-proxy:2.20.0"

        args = [
          "--port=5432",
          "--auto-iam-authn",
          containers.value,
        ]

        resources {
          limits = {
            cpu    = "0.5"
            memory = "256Mi"
          }
        }

        # サイドカーの起動完了を待ってからメインコンテナを起動
        # Cloud Run Service では depends_on と組み合わせて使用
        startup_probe {
          tcp_socket {
            port = 5432
          }
          initial_delay_seconds = 0
          period_seconds        = 2
          timeout_seconds       = 2
          failure_threshold     = 30
        }
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# Allow unauthenticated access if specified
resource "google_cloud_run_v2_service_iam_member" "public" {
  count = var.allow_unauthenticated ? 1 : 0

  project  = var.project_id
  location = var.location
  name     = google_cloud_run_v2_service.this.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
