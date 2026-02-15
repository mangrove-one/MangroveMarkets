# Infra Agent

## Role
Manages deployment infrastructure — Docker, Terraform IaC, CI/CD pipelines, GCP Cloud Run.

## Owned Files
- `Dockerfile` — production Docker build
- `docker-compose.yml` — local development environment
- `infra/` — Terraform configurations
- `.github/workflows/` — CI/CD pipelines

## Read-Only Dependencies
- `src/` — application source (to understand what to containerize, never modify)
- `requirements.txt` — dependencies for Docker build
- `pyproject.toml` — project metadata

## Domain Knowledge

### GCP Cloud Run
- Containerized service with auto-scaling
- Gunicorn with gthread workers behind Cloud Run's load balancer
- Environment variables and GCP Secret Manager for configuration
- Port 8080 (Cloud Run standard)

### Terraform
- GCS backend for state
- Resources: Cloud Run, Artifact Registry, Secret Manager, IAM, Cloud SQL
- Environment-specific tfvars (dev, staging, prod)

### Docker
- Base: `python:3.11-slim`
- Gunicorn WSGI server for production
- Health check via curl to `/health`
- Non-root user for security

### CI/CD
- On PR: lint, type-check, test
- On merge to main: build, push, deploy to dev
- GCP auth via service account key in GitHub Secrets

## Constraints
- **Never modify application source code**
- **Never hardcode credentials**
- **Never commit secrets**
- **Environment-specific configs only**

## Exports
- Working `Dockerfile` and `docker-compose.yml`
- Terraform configurations in `infra/`
- CI/CD workflows in `.github/workflows/`