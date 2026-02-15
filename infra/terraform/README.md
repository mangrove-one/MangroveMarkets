# MangroveMarkets Terraform Configuration

This directory contains Terraform configuration for deploying MangroveMarkets infrastructure to Google Cloud Platform.

## Overview

The Terraform configuration provisions:
- **Artifact Registry** repository for Docker images
- **Cloud Run** service for the application
- **Service Accounts** for Cloud Run and GitHub Actions deployments
- **IAM roles** for proper access control
- **Secret Manager** for application configuration
- **API enablement** for required GCP services

## Project Configuration

- **Project ID**: `mangrove-markets`
- **Service Name**: `mangrovemarkets`
- **Region**: `us-central1`
- **Artifact Registry**: `mangrove-markets-repo`

## Prerequisites

1. **GCP Project**: Ensure `mangrove-markets` project exists
2. **Terraform**: Install Terraform >= 1.5
3. **GCP Authentication**: Run `gcloud auth application-default login`
4. **Terraform State Bucket**: Create GCS bucket for state storage:
   ```bash
   gsutil mb -p mangrove-markets -l us-central1 gs://mangrove-markets-terraform-state
   gsutil versioning set on gs://mangrove-markets-terraform-state
   ```

## Files

- `main.tf` - Main infrastructure resources
- `variables.tf` - Input variables with defaults
- `outputs.tf` - Output values after apply
- `backend.tf` - Remote state configuration
- `backend-dev.hcl` - Backend config for dev environment
- `backend-prod.hcl` - Backend config for prod environment
- `environment-dev.tfvars` - Variable values for dev
- `environment-prod.tfvars` - Variable values for prod

## Usage

### Initialize Terraform

For development environment:
```bash
cd infra/terraform
terraform init -backend-config=backend-dev.hcl
```

For production environment:
```bash
cd infra/terraform
terraform init -backend-config=backend-prod.hcl
```

### Plan Changes

```bash
# Dev environment
terraform plan -var-file=environment-dev.tfvars

# Prod environment
terraform plan -var-file=environment-prod.tfvars
```

### Apply Changes

```bash
# Dev environment
terraform apply -var-file=environment-dev.tfvars

# Prod environment
terraform apply -var-file=environment-prod.tfvars
```

### View Outputs

```bash
terraform output
```

## Important Notes

### Critical: Always Use --project Flag

All `gcloud` commands in scripts and manual operations MUST use the `--project=mangrove-markets` flag. Never change the global gcloud config project setting.

**Correct:**
```bash
gcloud artifacts repositories list --project=mangrove-markets
gcloud run services list --project=mangrove-markets --region=us-central1
```

**Incorrect (DO NOT USE):**
```bash
gcloud config set project mangrove-markets  # Never do this
gcloud artifacts repositories list           # Missing --project flag
```

### GitHub Actions Service Account

After initial Terraform apply, you'll need to:

1. Create a service account key for GitHub Actions:
   ```bash
   gcloud iam service-accounts keys create github-actions-key.json \
     --iam-account=github-actions-deployer@mangrove-markets.iam.gserviceaccount.com \
     --project=mangrove-markets
   ```

2. Add the key content as a GitHub secret named `GCP_SA_KEY`

3. Delete the local key file:
   ```bash
   shred -u github-actions-key.json
   ```

### Managing Secrets

Application configuration secrets are stored in Secret Manager:

```bash
# Create a secret version (example)
echo '{"key": "value"}' | gcloud secrets versions add mangrovemarkets-config-dev \
  --data-file=- \
  --project=mangrove-markets

# View secret versions
gcloud secrets versions list mangrovemarkets-config-dev \
  --project=mangrove-markets
```

## Resource Naming Conventions

- Service accounts: `{purpose}-{environment}` (e.g., `mangrovemarkets-run-sa-dev`)
- Secrets: `mangrovemarkets-config-{environment}`
- Services: `mangrovemarkets` (prod) or `mangrovemarkets-{environment}` (non-prod)

## Terraform State

State is stored remotely in Google Cloud Storage:
- **Bucket**: `mangrove-markets-terraform-state`
- **Dev prefix**: `mangrovemarkets/dev`
- **Prod prefix**: `mangrovemarkets/prod`

State is managed separately per environment to prevent accidental cross-environment changes.

## Outputs

After applying, you'll get:
- `service_url` - Cloud Run service URL
- `artifact_registry_repo` - Full repository path
- `run_service_account_email` - Runtime service account
- `github_actions_service_account_email` - Deployment service account
- `secret_name` - Secret Manager secret ID for app config

## Troubleshooting

### Permission Denied Errors

Ensure your authenticated user has these roles on the `mangrove-markets` project:
- `roles/editor` or `roles/owner`
- `roles/iam.serviceAccountAdmin`
- `roles/resourcemanager.projectIamAdmin`

### State Lock Issues

If Terraform state is locked:
```bash
# Force unlock (use with caution)
terraform force-unlock <lock-id>
```

### API Not Enabled Errors

All required APIs are enabled by the `google_project_service` resources. Wait a few minutes after initial apply for APIs to fully activate.

## Next Steps

After infrastructure is provisioned:

1. Verify Cloud Run service is accessible via the output URL
2. Set up GitHub Actions secret `GCP_SA_KEY`
3. Push code to trigger deployment workflow
4. Add application configuration to Secret Manager
5. Monitor Cloud Run logs for application health

## References

- [Terraform GCP Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Artifact Registry Documentation](https://cloud.google.com/artifact-registry/docs)
- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
