# Configuration Files

Environment-specific configuration for MangroveMarkets.

## Files

- `local-config.json` - Local development (default)
- `dev-config.json` - Development environment
- `test-config.json` - Testing environment
- `prod-config.json` - Production environment

## Usage

The configuration system automatically loads the appropriate config file based on the `ENVIRONMENT` or `APP_ENV` environment variable. If neither is set, the app defaults to the 'local' environment.

```bash
# Use local config
ENVIRONMENT=local python src/app.py

# Use dev config
ENVIRONMENT=dev python src/app.py

# Use prod config
ENVIRONMENT=prod GCP_PROJECT_ID=your-project-id python src/app.py
```

## GCP Secret Manager Integration

Configuration values can reference secrets stored in GCP Secret Manager using the following syntax:

### Syntax

- `secret:<name>` - Returns entire secret as string
- `secret:<name>:<property>` - Returns specific property from JSON secret
- `secret:<name>:<property>:<version>` - Returns property with specific version (default: "latest")

### Examples

One GCP secret per environment (`mangrovemarkets-config-{env}`), containing all sensitive values as a JSON blob:

```json
{
  "DB_HOST": "secret:mangrovemarkets-config-prod:DB_HOST",
  "DB_PASSWORD": "secret:mangrovemarkets-config-prod:DB_PASSWORD",
  "JWT_SECRET": "secret:mangrovemarkets-config-prod:JWT_SECRET"
}
```

### Setting Up GCP Secrets

1. Create ONE JSON secret per environment in GCP Secret Manager:

```bash
# Create the prod secret with all sensitive config values
echo '{"DB_HOST":"10.0.0.1","DB_NAME":"mangrove_prod","DB_USER":"postgres","DB_PASSWORD":"secure123","JWT_SECRET":"your-jwt-secret","CLOUD_SQL_CONNECTION_NAME":"project:region:instance"}' | \
  gcloud secrets create mangrovemarkets-config-prod --data-file=- --project=mangrove-markets
```

2. Grant access to your service account:

```bash
gcloud secrets add-iam-policy-binding mangrovemarkets-config-prod \
  --member="serviceAccount:your-sa@project.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=mangrove-markets
```

3. Set the GCP_PROJECT_ID environment variable:

```bash
export GCP_PROJECT_ID=your-gcp-project-id
```

### Required GCP Setup

For production deployment:

1. **GCP Project**: Set `GCP_PROJECT_ID` environment variable
2. **Service Account**: Must have `roles/secretmanager.secretAccessor` role
3. **Authentication**: Use Application Default Credentials (ADC) or service account key

### Secret Format

For JSON secrets, structure them as key-value pairs:

```json
{
  "username": "postgres",
  "password": "secure-password",
  "host": "10.0.0.1",
  "port": 5432,
  "database": "mangrove_prod"
}
```

Then reference properties in config:

```json
{
  "DB_HOST": "secret:mangrovemarkets-config-prod:DB_HOST",
  "DB_USER": "secret:mangrovemarkets-config-prod:DB_USER",
  "DB_PASSWORD": "secret:mangrovemarkets-config-prod:DB_PASSWORD"
}
```

## Adding New Configuration Values

1. Add the key to `configuration-keys.json` in the `required_keys` array
2. Add the value to ALL environment config JSON files (`local`, `dev`, `test`, `prod`)
3. The key will be automatically set as an attribute via `setattr()` -- no code changes needed in `config.py`
4. Update this README with documentation

## Testing

The config system includes a reset mechanism for testing:

```python
from src.shared.config import _Config

# Reset config singleton for clean test
# The singleton uses __new__ for instance control; reset() sets _instance = None
_Config.reset()
```

## Security Notes

- Never commit secrets directly to config files
- Use `secret:` syntax for all sensitive values in production
- Keep local/dev/test configs with non-sensitive defaults
- Rotate secrets regularly in GCP Secret Manager
- Monitor secret access via GCP Cloud Audit Logs
