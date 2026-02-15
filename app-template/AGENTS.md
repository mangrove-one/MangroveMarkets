# App Template Deployment Guide

This file documents packaging, configuration, and deployment for the app template.

## Packaging
- Service: `app/` (Flask + Gunicorn)
- Docker image: `Dockerfile` (single service container)
- Local dev: `docker-compose.yml`

## Configuration
- Config loader: `app/app_core/config.py`
- Config files: `app/app_core/config/<env>-config.json`
- Required keys: `app/app_core/config/configuration-keys.json`
- Secrets: values prefixed with `secret:<secret-name>:<property>` resolve from Secret Manager at runtime.

## One-Time GCP Setup (Single Project)
1. Create a GCP project and attach billing.
2. Create a Terraform state bucket.
3. Update:
   - `infra/terraform/backend-dev.hcl`
   - `infra/terraform/environment-dev.tfvars`
4. Run Terraform:
```bash
cd infra/terraform
terraform init -backend-config=backend-dev.hcl
terraform apply -var-file=environment-dev.tfvars
```
5. Populate Secret Manager values:
```bash
echo '{"db_password":"<password>","jwt_secret":"<secret>","admin_emails":"admin@example.com"}' | \
  gcloud secrets versions add app-config-dev --data-file=-
```

## Deploy
Use the workflow template at `.github/workflows/deploy-cloudrun.yaml` (copy to repo root for use).

## Runtime Verification
- Health check: `GET /health`
- Hello API:
  - `POST /api/guess` with `{ "name": "Avery" }`
  - `GET /api/guess/Avery`

## Notes
- Single project + single Cloud Run service only.
- Auth is stubbed; `AUTH_ENABLED=false` disables auth checks.
