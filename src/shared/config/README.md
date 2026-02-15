# Configuration Files

Environment-specific configuration for MangroveMarkets.

## Files

- `local-config.json` - Local development (default)
- `dev-config.json` - Development environment
- `test-config.json` - Testing environment
- `prod-config.json` - Production environment

## Usage

The configuration system automatically loads the appropriate config file based on the `ENVIRONMENT` or `APP_ENV` environment variable. If neither is set, it defaults to `local`.

```bash
# Use local config (default)
python src/app.py

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

```json
{
  "DB_PASSWORD": "secret:mangrove-prod-db:password",
  "JWT_SECRET": "secret:mangrove-prod-auth:jwt_secret",
  "API_KEY": "secret:third-party-api-keys:openai"
}
```

### Setting Up GCP Secrets

1. Create secrets in GCP Secret Manager:

```bash
# Create a JSON secret
echo '{"username":"postgres","password":"secure123","host":"10.0.0.1","database":"mangrove"}' | \
  gcloud secrets create mangrove-prod-db --data-file=-

# Create a simple string secret
echo 'your-jwt-secret-here' | \
  gcloud secrets create mangrove-prod-auth --data-file=-
```

2. Grant access to your service account:

```bash
gcloud secrets add-iam-policy-binding mangrove-prod-db \
  --member="serviceAccount:your-sa@project.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
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
  "DB_HOST": "secret:mangrove-prod-db:host",
  "DB_USER": "secret:mangrove-prod-db:username",
  "DB_PASSWORD": "secret:mangrove-prod-db:password"
}
```

## Environment Variable Overrides

Environment variables always take precedence over config files. They also support the secret syntax:

```bash
export DB_PASSWORD="secret:mangrove-prod-db:password"
export ENVIRONMENT=prod
python src/app.py
```

## Adding New Configuration Values

1. Add the property to the `Config` class in `src/shared/config.py`
2. Use the `_get_value()` method for automatic secret resolution
3. Add the value to all environment config files
4. Update this README with documentation

Example:

```python
@property
def NEW_CONFIG_VALUE(self) -> str:
    return self._get_value("NEW_CONFIG_VALUE", "NEW_CONFIG_VALUE", "default-value")
```

## Testing

The config system includes a reset mechanism for testing:

```python
from src.shared.config import Config
from src.shared.gcp_secret_utils import reset_secret_manager

# Reset config for clean test
Config.reset()
reset_secret_manager()

# Get fresh instance
config = Config.get()
```

## Security Notes

- Never commit secrets directly to config files
- Use `secret:` syntax for all sensitive values in production
- Keep local/dev/test configs with non-sensitive defaults
- Rotate secrets regularly in GCP Secret Manager
- Monitor secret access via GCP Cloud Audit Logs
