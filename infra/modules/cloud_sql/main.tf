# -----------------------------------------------------------------------------
# Cloud SQL Module (PostgreSQL)
# Reference: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/sql_database_instance
# -----------------------------------------------------------------------------

resource "google_sql_database_instance" "this" {
  project             = var.project_id
  name                = var.instance_name
  database_version    = "POSTGRES_17"
  region              = var.region
  deletion_protection = var.deletion_protection

  settings {
    tier              = "db-custom-1-3840"
    edition           = "ENTERPRISE"
    availability_type = var.availability_type
    activation_policy = var.activation_policy
    disk_size         = 10
    disk_type         = "PD_SSD"
    disk_autoresize   = true

    backup_configuration {
      enabled                        = true
      start_time                     = "18:00"
      location                       = var.region
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7
      backup_retention_settings {
        retained_backups = var.retained_backups
        retention_unit   = "COUNT"
      }
    }

    ip_configuration {
      ipv4_enabled = true
      ssl_mode     = "ENCRYPTED_ONLY"
    }

    database_flags {
      name  = "cloudsql.iam_authentication"
      value = "on"
    }

    database_flags {
      name  = "log_connections"
      value = "on"
    }

    database_flags {
      name  = "log_statement"
      value = "mod"
    }

    maintenance_window {
      day          = 7
      hour         = 17
      update_track = "stable"
    }

    insights_config {
      query_insights_enabled  = true
      query_string_length     = 1024
      record_application_tags = true
      record_client_address   = true
      query_plans_per_minute  = 5
    }
  }

  timeouts {
    create = "90m"
    delete = "60m"
    update = "90m"
  }
}

# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------

resource "google_sql_database" "this" {
  project   = var.project_id
  name      = var.database_name
  instance  = google_sql_database_instance.this.name
  charset   = "UTF8"
  collation = "en_US.UTF8"
}

# -----------------------------------------------------------------------------
# IAM Users
# -----------------------------------------------------------------------------

resource "google_sql_user" "iam_users" {
  for_each = toset(var.iam_users)

  project  = var.project_id
  name     = "${each.value}@${var.project_id}.iam"
  instance = google_sql_database_instance.this.name
  type     = "CLOUD_IAM_SERVICE_ACCOUNT"
}
