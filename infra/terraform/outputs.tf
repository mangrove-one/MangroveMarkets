output "service_url" {
  description = "Cloud Run service URL"
  value       = google_cloud_run_v2_service.app.uri
}

output "artifact_registry_repo" {
  description = "Artifact Registry repository name"
  value       = google_artifact_registry_repository.repo.name
}

output "run_service_account_email" {
  description = "Cloud Run service account email"
  value       = google_service_account.run_sa.email
}

output "github_actions_service_account_email" {
  description = "GitHub Actions service account email"
  value       = google_service_account.github_actions_sa.email
}

output "secret_name" {
  description = "Secret Manager secret name for app configuration"
  value       = google_secret_manager_secret.app_config.secret_id
}
