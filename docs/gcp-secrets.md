# GCP Secret Manager Integration

MangroveMarkets uses Google Cloud Platform Secret Manager for secure credential management in production environments.

## Overview

The GCP Secret Manager integration allows configuration values to reference secrets stored in GCP Secret Manager using a simple syntax. This keeps sensitive credentials out of config files and environment variables while maintaining ease of use.

## Features

- **Secret References**: Use `secret:<name>:<property>` syntax in config files
- **Automatic Resolution**: Secrets are resolved at config load time
- **Caching**: Fetched secrets are cached to minimize API calls
- **Fallback Support**: Falls back to plain values if secret resolution fails
- **Environment Variable Support**: Secret syntax works in env vars too
- **JSON Secrets**: Store structured credentials as JSON and extract properties

## Setup

### 1. Install Dependencies

Dependencies are already in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 2. Create GCP Secrets

Create secrets in GCP Secret Manager using the `gcloud` CLI:

```bash
# Set your project
export GCP_PROJECT_ID=your-project-id

# Create a JSON secret for database credentials
echo '{
  "host": "10.0.0.1",
  "database": "mangrove_prod",
  "username": "mangrove_user",
  "password": "super-secret-password"
}' | gcloud secrets create mangrove-prod-db --data-file=-

# Create a simple string secret
echo "your-jwt-secret-here" | \
  gcloud secrets create mangrove-prod-jwt --data-file=-
```

### 3. Grant Access

Give your service account access to secrets:

```bash
# Get your service account email
SA_EMAIL=your-sa@your-project.iam.gserviceaccount.com

# Grant access to specific secret
gcloud secrets add-iam-policy-binding mangrove-prod-db \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"

# Or grant access to all secrets (project-wide)
gcloud projects add-iam-policy-binding ${GCP_PROJECT_ID} \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"
```

### 4. Configure Authentication

#### Option A: Application Default Credentials (Recommended)

For Cloud Run, GKE, or GCE:

```bash
# No additional setup needed - uses instance service account
```

For local development:

```bash
gcloud auth application-default login
```

#### Option B: Service Account Key

```bash
# Create and download key
gcloud iam service-accounts keys create key.json \
  --iam-account=${SA_EMAIL}

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
```

**Warning**: Never commit service account keys to git!

### 5. Set Environment Variables

```bash
export GCP_PROJECT_ID=your-project-id
export ENVIRONMENT=prod
```

## Usage

### Config File Syntax

In your environment config files (e.g., `prod-config.json`):

```json
{
  "DB_HOST": "secret:mangrove-prod-db:host",
  "DB_NAME": "secret:mangrove-prod-db:database",
  "DB_USER": "secret:mangrove-prod-db:username",
  "DB_PASSWORD": "secret:mangrove-prod-db:password",
  "JWT_SECRET": "secret:mangrove-prod-jwt"
}
```

### Secret Reference Formats

1. **Entire Secret** (string secret):
   ```
   secret:<secret-name>
   ```
   Example: `secret:api-key` returns the full secret value

2. **JSON Property** (extract from JSON secret):
   ```
   secret:<secret-name>:<property>
   ```
   Example: `secret:db-creds:password` returns just the password field

3. **Specific Version** (with version number):
   ```
   secret:<secret-name>:<property>:<version>
   ```
   Example: `secret:db-creds:password:5` returns version 5

   Version defaults to `latest` if not specified.

### Environment Variables

Secret syntax also works in environment variables:

```bash
export DB_PASSWORD="secret:mangrove-prod-db:password"
export ENVIRONMENT=prod
python src/app.py
```

### Programmatic Access

Direct access to secrets in Python code:

```python
from src.shared.gcp_secret_utils import GCPSecretManager, resolve_secret_value

# Get entire secret
manager = GCPSecretManager()
secret = manager.get_secret("my-secret")

# Get JSON secret
secret_json = manager.get_secret_json("my-secret")

# Get specific property
password = manager.get_secret_property("db-creds", "password")

# Or use resolve_secret_value for syntax parsing
password = resolve_secret_value("secret:db-creds:password")
```

## Secret Organization

### Recommended Structure

Organize secrets by component and environment:

```
mangrove-prod-db          # Database credentials
mangrove-prod-auth        # Authentication secrets
mangrove-prod-xrpl        # XRPL wallet seeds
mangrove-prod-external    # External API keys

mangrove-dev-db           # Dev environment
mangrove-dev-auth         # Dev environment
```

### JSON Secret Format

For related credentials, use JSON:

```json
{
  "host": "db.example.com",
  "port": 5432,
  "database": "mangrove",
  "username": "mangrove_app",
  "password": "secure-password",
  "ssl_mode": "require"
}
```

Then reference properties:

```json
{
  "DB_HOST": "secret:mangrove-prod-db:host",
  "DB_PORT": "secret:mangrove-prod-db:port",
  "DB_NAME": "secret:mangrove-prod-db:database",
  "DB_USER": "secret:mangrove-prod-db:username",
  "DB_PASSWORD": "secret:mangrove-prod-db:password"
}
```

## Security Best Practices

1. **Never Commit Secrets**: Keep secrets out of git, even in config files
2. **Use IAM Roles**: Grant least-privilege access via IAM
3. **Rotate Regularly**: Update secrets periodically
4. **Audit Access**: Enable Cloud Audit Logs for secret access
5. **Separate Environments**: Use different secrets for dev/test/prod
6. **Version Secrets**: Use secret versions for rollback capability
7. **Secure Service Accounts**: Protect service account keys carefully

## Troubleshooting

### Error: GCP project ID not provided

Set the `GCP_PROJECT_ID` environment variable:

```bash
export GCP_PROJECT_ID=your-project-id
```

### Error: Secret not found

1. Check the secret exists:
   ```bash
   gcloud secrets describe mangrove-prod-db
   ```

2. Verify you have access:
   ```bash
   gcloud secrets get-iam-policy mangrove-prod-db
   ```

### Error: Permission denied

Grant the secretAccessor role:

```bash
gcloud secrets add-iam-policy-binding mangrove-prod-db \
  --member="serviceAccount:your-sa@project.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Error: Property not found in secret

For JSON secrets, verify the property exists:

```bash
gcloud secrets versions access latest --secret=mangrove-prod-db
```

The output should show your JSON with the expected property.

### Secrets Not Resolving in Development

In local development, ensure you have Application Default Credentials:

```bash
gcloud auth application-default login
```

Or use a service account key:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
```

## Cost Considerations

Secret Manager pricing (as of 2026):

- **Storage**: $0.06 per secret version per month
- **Access**: $0.03 per 10,000 access operations

With caching enabled (default), MangroveMarkets minimizes access costs by caching resolved secrets in memory.

## Migration Guide

### From Environment Variables

**Before:**
```bash
export DB_PASSWORD=my-password
```

**After:**

1. Create secret:
   ```bash
   echo "my-password" | gcloud secrets create mangrove-prod-db-pass --data-file=-
   ```

2. Update config:
   ```json
   {
     "DB_PASSWORD": "secret:mangrove-prod-db-pass"
   }
   ```

### From Config Files

**Before:**
```json
{
  "DB_PASSWORD": "plain-text-password"
}
```

**After:**

1. Create secret:
   ```bash
   echo "plain-text-password" | gcloud secrets create mangrove-prod-db-pass --data-file=-
   ```

2. Update config:
   ```json
   {
     "DB_PASSWORD": "secret:mangrove-prod-db-pass"
   }
   ```

3. Remove old value from git history (if committed):
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch prod-config.json" --prune-empty --tag-name-filter cat -- --all
   ```

## Testing

### Unit Tests

Run the GCP Secret Manager tests:

```bash
pytest tests/shared/test_gcp_secret_utils.py -v
pytest tests/shared/test_config_secrets.py -v
```

### Manual Testing

1. Create a test secret:
   ```bash
   echo "test-value" | gcloud secrets create test-secret --data-file=-
   ```

2. Test resolution:
   ```python
   from src.shared.gcp_secret_utils import resolve_secret_value

   value = resolve_secret_value("secret:test-secret")
   print(f"Resolved: {value}")
   ```

3. Clean up:
   ```bash
   gcloud secrets delete test-secret
   ```

## References

- [GCP Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
- [Python Client Library](https://cloud.google.com/python/docs/reference/secretmanager/latest)
- [IAM Roles for Secret Manager](https://cloud.google.com/secret-manager/docs/access-control)
- [Best Practices](https://cloud.google.com/secret-manager/docs/best-practices)
