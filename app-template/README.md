# App Template (Single Project, Single Service)

This template is aligned to a **single GCP project** and **single Cloud Run service**.

## What You Get
- Flask API skeleton with health check
- Hello-world routes + service layer (POST + GET)
- Config loading with `ENVIRONMENT`/`APP_ENV` and Secret Manager support
- Minimal auth scaffolding (disabled by default)
- Terraform for **one** Cloud Run service + Artifact Registry + Secret Manager
- GitHub Actions workflow for build + deploy

## Local Quick Start
```bash
cd app-template
cp .env.example .env
cp app/app_core/config/local-example-config.json app/app_core/config/local-config.json
docker compose up -d --build
curl http://localhost:8080/health
```

## API Demo
```bash
curl -X POST http://localhost:8080/api/guess -H "Content-Type: application/json" -d '{"name":"Avery"}'
curl http://localhost:8080/api/guess/Avery
```

## GCP Setup (One-Time)
1. Create a GCP project and attach billing.
2. Create a Terraform state bucket.
3. Update:
   - `infra/terraform/backend-dev.hcl`
   - `infra/terraform/environment-dev.tfvars`
4. Provision infra:
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
Use the workflow template at `app-template/.github/workflows/deploy-cloudrun.yaml`.

## File Map
- `app/app.py` - Flask entrypoint
- `app/app_core/` - Config, routes, services, utils
- `Dockerfile` - Container build
- `docker-compose.yml` - Local dev
- `infra/terraform/` - IaC for **single** service
