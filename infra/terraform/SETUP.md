# MangroveMarkets Infrastructure Setup

This document provides step-by-step instructions for setting up the MangroveMarkets infrastructure using Terraform.

## Initial Setup

### 1. Authenticate to GCP

```bash
gcloud auth application-default login
```

This creates credentials that Terraform can use.

### 2. Create Terraform State Bucket

The state bucket must be created before running Terraform:

```bash
# Create the bucket
gsutil mb -p mangrove-markets -l us-central1 gs://mangrove-markets-terraform-state

# Enable versioning for state history
gsutil versioning set on gs://mangrove-markets-terraform-state
```

### 3. Verify Project Access

Ensure you have the necessary permissions:

```bash
# List projects to verify access
gcloud projects list --project=mangrove-markets

# Check your roles
gcloud projects get-iam-policy mangrove-markets \
    --flatten="bindings[].members" \
    --format="table(bindings.role)" \
    --filter="bindings.members:user:YOUR_EMAIL" \
    --project=mangrove-markets
```

You should have `roles/editor` or `roles/owner` and `roles/iam.serviceAccountAdmin`.

## Deploying Infrastructure

### Using the Helper Script (Recommended)

The `terraform.sh` helper script ensures consistent usage and project flag enforcement:

```bash
# Initialize for dev environment
./terraform.sh init dev

# Plan changes
./terraform.sh plan dev

# Apply changes
./terraform.sh apply dev

# View outputs
./terraform.sh output dev
```

For production:

```bash
./terraform.sh init prod
./terraform.sh plan prod
./terraform.sh apply prod
```

### Manual Terraform Commands

If you prefer to run Terraform directly:

```bash
# Development environment
cd infra/terraform
terraform init -backend-config=backend-dev.hcl
terraform plan -var-file=environment-dev.tfvars
terraform apply -var-file=environment-dev.tfvars

# Production environment
terraform init -backend-config=backend-prod.hcl
terraform plan -var-file=environment-prod.tfvars
terraform apply -var-file=environment-prod.tfvars
```

## Post-Deployment Setup

### 1. Get Infrastructure Outputs

```bash
./terraform.sh output dev
```

This shows:
- `service_url` - Your Cloud Run service URL
- `artifact_registry_repo` - Docker repository path
- `run_service_account_email` - Runtime service account
- `github_actions_service_account_email` - Deployment service account
- `secret_name` - Secret Manager secret for config

### 2. Configure GitHub Actions

Create a service account key for GitHub Actions:

```bash
# Create key
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=github-actions-deployer@mangrove-markets.iam.gserviceaccount.com \
    --project=mangrove-markets

# View the key content (to copy)
cat github-actions-key.json
```

Add to GitHub:
1. Go to: https://github.com/YOUR_ORG/MangroveMarkets/settings/secrets/actions
2. Create new secret: `GCP_SA_KEY`
3. Paste the entire JSON content

Delete the local key:
```bash
shred -u github-actions-key.json
```

### 3. Add Application Configuration

Store your application configuration in Secret Manager:

```bash
# Create initial configuration
cat > config.json <<EOF
{
  "xrpl_network": "testnet",
  "ipfs_gateway": "https://ipfs.io",
  "log_level": "INFO"
}
EOF

# Add to Secret Manager
gcloud secrets versions add mangrovemarkets-config-dev \
    --data-file=config.json \
    --project=mangrove-markets

# Clean up
rm config.json
```

### 4. Verify Cloud Run Deployment

```bash
# Get service URL
SERVICE_URL=$(terraform output -raw service_url)

# Test the service
curl ${SERVICE_URL}/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-02-15T13:44:00Z"
}
```

## Environment Management

### Development Environment

The dev environment (`mangrovemarkets-dev`) is for testing:
- **Separate service** from production
- **Lower resource limits** (512Mi memory, 1 CPU)
- **Auto-scaled** to zero when idle
- **Separate state** in `mangrovemarkets/dev` prefix

### Production Environment

The production environment (`mangrovemarkets`) is for live traffic:
- **Production service** at `mangrovemarkets`
- **Same resource configuration** but can be scaled independently
- **Separate state** in `mangrovemarkets/prod` prefix
- **Requires confirmation** for apply/destroy operations

## Infrastructure Components

### Artifact Registry

Docker images are stored in `mangrove-markets-repo`:
```bash
# List images
gcloud artifacts docker images list \
    us-central1-docker.pkg.dev/mangrove-markets/mangrove-markets-repo \
    --project=mangrove-markets

# Delete old images
gcloud artifacts docker images delete \
    us-central1-docker.pkg.dev/mangrove-markets/mangrove-markets-repo/mangrovemarkets:TAG \
    --project=mangrove-markets
```

### Cloud Run

The service runs on Cloud Run with:
- **Port**: 8080
- **Memory**: 512Mi
- **CPU**: 1
- **Min instances**: 0
- **Max instances**: 10
- **Timeout**: 120s
- **Public access**: Enabled

### Service Accounts

Two service accounts are created:

1. **Runtime SA** (`mangrovemarkets-run-sa-{env}`):
   - Used by Cloud Run to execute your application
   - Has access to Secret Manager
   - Can write logs

2. **Deployer SA** (`github-actions-deployer`):
   - Used by GitHub Actions for deployments
   - Can manage Cloud Run services
   - Can push to Artifact Registry

### Secret Manager

Application configuration is stored in Secret Manager:
- Secret: `mangrovemarkets-config-{env}`
- Auto-replication across regions
- Accessible by runtime service account
- Versioned for rollback capability

## Maintenance

### Updating Infrastructure

```bash
# Make changes to .tf files
vim infra/terraform/main.tf

# Preview changes
./terraform.sh plan dev

# Apply changes
./terraform.sh apply dev
```

### Viewing State

```bash
# List resources
terraform state list

# Show specific resource
terraform state show google_cloud_run_v2_service.app

# Pull remote state
terraform state pull > state.json
```

### Destroying Infrastructure

**WARNING**: This will delete all infrastructure!

```bash
# Development environment
./terraform.sh destroy dev

# Production (requires environment name confirmation)
./terraform.sh destroy prod
```

## Troubleshooting

### "Backend initialization required"

You need to run `terraform init`:
```bash
./terraform.sh init dev
```

### "Error acquiring the state lock"

Someone else is running Terraform. Wait for them to finish, or force unlock (dangerous):
```bash
terraform force-unlock LOCK_ID
```

### "Permission denied" errors

Check your GCP roles:
```bash
gcloud projects get-iam-policy mangrove-markets \
    --flatten="bindings[].members" \
    --filter="bindings.members:user:$(gcloud config get-value account)" \
    --project=mangrove-markets
```

### "API not enabled"

Terraform should enable APIs automatically. If not:
```bash
gcloud services enable run.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com \
    --project=mangrove-markets
```

## Security Best Practices

1. **Never commit service account keys** to git
2. **Use --project flag** in all gcloud commands (never change global config)
3. **Rotate service account keys** regularly (every 90 days)
4. **Audit IAM permissions** periodically
5. **Enable versioning** on state bucket (already done)
6. **Use separate environments** for dev/prod
7. **Review Terraform plans** before applying

## CI/CD Integration

GitHub Actions workflow (`.github/workflows/deploy-cloudrun.yaml`) automatically:
1. Builds Docker image
2. Pushes to Artifact Registry
3. Deploys to Cloud Run
4. Uses the `github-actions-deployer` service account

All gcloud commands in the workflow include `--project=mangrove-markets` flag.

## Cost Estimation

Expected monthly costs (approximate):
- **Cloud Run**: $0-5 (auto-scales to zero)
- **Artifact Registry**: $0.10/GB storage
- **Secret Manager**: $0.06 per secret/month
- **State Bucket**: <$1/month

Total: ~$5-10/month for development, scales with usage.

## Next Steps

1. Deploy infrastructure: `./terraform.sh apply dev`
2. Configure GitHub Actions secret
3. Push code to trigger deployment
4. Add custom domain mapping (see `docs/domain-setup.md`)
5. Configure monitoring and alerting

## Support

For issues:
1. Check Terraform output for error messages
2. Verify GCP permissions
3. Review Cloud Run logs: `gcloud run services logs read mangrovemarkets-dev --project=mangrove-markets`
4. Check GitHub Actions logs for deployment issues
