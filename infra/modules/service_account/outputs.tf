# -----------------------------------------------------------------------------
# Outputs
# -----------------------------------------------------------------------------

output "id" {
  description = "サービスアカウントの ID（projects/{project}/serviceAccounts/{email} 形式）"
  value       = google_service_account.this.id
}

output "email" {
  description = "サービスアカウントのメールアドレス"
  value       = google_service_account.this.email
}

output "name" {
  description = "サービスアカウントの完全修飾名"
  value       = google_service_account.this.name
}

output "unique_id" {
  description = "サービスアカウントの一意の ID"
  value       = google_service_account.this.unique_id
}

output "member" {
  description = "サービスアカウントの Identity（serviceAccount:{email} 形式）"
  value       = google_service_account.this.member
}
