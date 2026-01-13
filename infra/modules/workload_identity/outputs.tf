# -----------------------------------------------------------------------------
# Outputs
# -----------------------------------------------------------------------------

output "pool_name" {
  description = "Workload Identity Pool のフルネーム"
  value       = google_iam_workload_identity_pool.this.name
}

output "pool_id" {
  description = "Workload Identity Pool の ID"
  value       = google_iam_workload_identity_pool.this.workload_identity_pool_id
}

output "provider_name" {
  description = "Workload Identity Provider のフルネーム"
  value       = google_iam_workload_identity_pool_provider.this.name
}

output "provider_id" {
  description = "Workload Identity Provider の ID"
  value       = google_iam_workload_identity_pool_provider.this.workload_identity_pool_provider_id
}
