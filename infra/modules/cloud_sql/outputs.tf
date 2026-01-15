# -----------------------------------------------------------------------------
# Cloud SQL Module - Outputs
# -----------------------------------------------------------------------------

output "instance_name" {
  description = "Cloud SQL インスタンス名"
  value       = google_sql_database_instance.this.name
}

output "connection_name" {
  description = "Cloud SQL 接続名（project:region:instance 形式）"
  value       = google_sql_database_instance.this.connection_name
}

output "private_ip_address" {
  description = "Cloud SQL プライベート IP アドレス"
  value       = google_sql_database_instance.this.private_ip_address
}

output "public_ip_address" {
  description = "Cloud SQL パブリック IP アドレス"
  value       = google_sql_database_instance.this.public_ip_address
}

output "database_name" {
  description = "データベース名"
  value       = google_sql_database.this.name
}

output "self_link" {
  description = "Cloud SQL インスタンスの self_link"
  value       = google_sql_database_instance.this.self_link
}
