# GCP Secrets Quick Reference

Quick reference for using GCP Secret Manager with MangroveMarkets.

## Syntax

```
secret:<name>                    # Entire secret
secret:<name>:<property>         # JSON property
secret:<name>:<property>:<version>  # Specific version
```

## Setup (One-time)

```bash
# 1. Set project
export GCP_PROJECT_ID=your-project-id

# 2. Authenticate
gcloud auth application-default login

# 3. Create secrets
echo '{"username":"user","password":"pass"}' | \
  gcloud secrets create my-secret --data-file=-

# 4. Grant access (if using service account)
gcloud secrets add-iam-policy-binding my-secret \
  --member="serviceAccount:your-sa@project.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## Usage in Config Files

**src/shared/config/prod-config.json:**
```json
{
  "DB_PASSWORD": "secret:mangrovemarkets-config-prod:DB_PASSWORD",
  "JWT_SECRET": "secret:mangrovemarkets-config-prod:JWT_SECRET"
}
```

## Usage in Environment

```bash
export DB_PASSWORD="secret:mangrovemarkets-config-prod:DB_PASSWORD"
export ENVIRONMENT=prod
python src/app.py
```

## Usage in Code

```python
from src.shared.gcp_secret_utils import GCPSecretManager, resolve_secret_value

# Direct access
manager = GCPSecretManager()
secret = manager.get_secret("my-secret")
password = manager.get_secret_property("db-creds", "password")

# Resolve syntax
value = resolve_secret_value("secret:db-creds:password")

# Via config
from src.shared.config import app_config
db_pass = app_config.DB_PASSWORD  # Auto-resolved if configured
```

## Common Commands

```bash
# List secrets
gcloud secrets list

# View secret (latest version)
gcloud secrets versions access latest --secret=my-secret

# Create secret from file
gcloud secrets create my-secret --data-file=secret.txt

# Create secret from stdin
echo "secret-value" | gcloud secrets create my-secret --data-file=-

# Update secret (creates new version)
echo "new-value" | gcloud secrets versions add my-secret --data-file=-

# Delete secret
gcloud secrets delete my-secret

# View IAM policy
gcloud secrets get-iam-policy my-secret

# Grant access
gcloud secrets add-iam-policy-binding my-secret \
  --member="serviceAccount:sa@project.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## Config Files by Environment

- `local-config.json` - Local dev (no secrets)
- `dev-config.json` - Dev environment
- `test-config.json` - Test environment
- `prod-config.json` - Production (uses secrets)

## Environment Variables

```bash
GCP_PROJECT_ID       # Required: Your GCP project ID
ENVIRONMENT          # Optional: dev/test/prod/local (default: local)
APP_ENV             # Alternative to ENVIRONMENT
GOOGLE_APPLICATION_CREDENTIALS  # Optional: Path to service account key
```

## Troubleshooting

| Error | Solution |
|-------|----------|
| "GCP project ID not provided" | Set `GCP_PROJECT_ID` env var |
| "Secret not found" | Create secret with `gcloud secrets create` |
| "Permission denied" | Grant `roles/secretmanager.secretAccessor` |
| "Property not found" | Check JSON structure with `gcloud secrets versions access` |
| "Module not found" | Run `pip install -r requirements.txt` |

## Security Checklist

- Never commit secrets to git
- Use `.gitignore` for credential files
- Separate secrets by environment (dev/test/prod)
- Use least-privilege IAM roles
- Rotate secrets regularly
- Enable Cloud Audit Logs
- Use service account keys only when necessary
- Delete unused secrets

## Examples

See `examples/gcp_secrets_example.py` for working examples.

```bash
python examples/gcp_secrets_example.py
```

## Full Documentation

See `docs/gcp-secrets.md` for complete documentation.
