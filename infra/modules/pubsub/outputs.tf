# -----------------------------------------------------------------------------
# Pub/Sub Module - Outputs
# -----------------------------------------------------------------------------

output "topic_id" {
  description = "Pub/Sub トピック ID"
  value       = google_pubsub_topic.this.id
}

output "topic_name" {
  description = "Pub/Sub トピック名"
  value       = google_pubsub_topic.this.name
}

output "subscription_id" {
  description = "Pub/Sub サブスクリプション ID"
  value       = google_pubsub_subscription.this.id
}

output "subscription_name" {
  description = "Pub/Sub サブスクリプション名"
  value       = google_pubsub_subscription.this.name
}

