#!/usr/bin/env python3
"""Example script demonstrating GCP Secret Manager integration.

This script shows how to:
1. Access secrets directly via GCPSecretManager
2. Use secret references in configuration
3. Resolve secret syntax programmatically

Prerequisites:
- GCP_PROJECT_ID environment variable set
- gcloud auth configured
- Secrets created in GCP Secret Manager
"""
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.shared.gcp_secret_utils import (
    GCPSecretManager,
    resolve_secret_value,
    reset_secret_manager,
)
from src.shared.config import Config


def example_direct_access():
    """Example 1: Direct access to secrets."""
    print("\n=== Example 1: Direct Secret Access ===")

    try:
        manager = GCPSecretManager()

        # Get a simple string secret
        print("\nFetching string secret...")
        # secret = manager.get_secret("example-secret")
        # print(f"Secret value: {secret}")

        # Get a JSON secret
        print("\nFetching JSON secret...")
        # secret_json = manager.get_secret_json("example-json-secret")
        # print(f"JSON secret: {secret_json}")

        # Get specific property from JSON secret
        print("\nFetching property from JSON secret...")
        # password = manager.get_secret_property("db-credentials", "password")
        # print(f"Password: {password}")

        print("\nNote: Uncomment lines above and create secrets to test")

    except ValueError as e:
        print(f"Error: {e}")
        print("\nTo test this, create a secret first:")
        print('  echo "test-value" | gcloud secrets create example-secret --data-file=-')


def example_resolve_syntax():
    """Example 2: Resolve secret syntax."""
    print("\n=== Example 2: Resolve Secret Syntax ===")

    # These would resolve if secrets exist
    test_values = [
        ("plain-value", "Plain value (no secret)"),
        ("secret:my-secret", "Entire secret"),
        ("secret:db-creds:password", "JSON property"),
        ("secret:db-creds:password:5", "Specific version"),
    ]

    for value, description in test_values:
        print(f"\n{description}: '{value}'")
        try:
            resolved = resolve_secret_value(value)
            if resolved == value:
                print(f"  → Not a secret reference, returned as-is")
            else:
                print(f"  → Resolved to: {resolved}")
        except ValueError as e:
            print(f"  → Error: {e}")


def example_config_integration():
    """Example 3: Config integration with secrets."""
    print("\n=== Example 3: Config Integration ===")

    # Reset to get fresh config
    Config.reset()
    reset_secret_manager()

    config = Config.get()

    print(f"\nEnvironment: {config.ENVIRONMENT}")
    print(f"DB Host: {config.DB_HOST}")
    print(f"DB Name: {config.DB_NAME}")
    print(f"DB User: {config.DB_USER}")

    # Password would be resolved from secret if configured
    print(f"DB Password: {'*' * len(config.DB_PASSWORD)} (hidden)")

    print("\nNote: To use secrets in config:")
    print("1. Edit src/shared/config/{env}-config.json")
    print('2. Set value to: "secret:mangrove-prod-db:password"')
    print("3. Create the secret in GCP Secret Manager")


def example_create_test_secret():
    """Example 4: Helper to create a test secret."""
    print("\n=== Example 4: Create Test Secret ===")

    project_id = os.environ.get("GCP_PROJECT_ID")
    if not project_id:
        print("Error: GCP_PROJECT_ID not set")
        return

    print(f"\nProject ID: {project_id}")
    print("\nTo create a test secret, run:")
    print()
    print("  # Simple string secret")
    print('  echo "test-value-123" | \\')
    print("    gcloud secrets create mangrove-test-secret --data-file=-")
    print()
    print("  # JSON secret")
    print("  echo '{")
    print('    "username": "test_user",')
    print('    "password": "test_pass_123",')
    print('    "host": "localhost",')
    print('    "database": "test_db"')
    print("  }' | \\")
    print("    gcloud secrets create mangrove-test-db-creds --data-file=-")
    print()
    print("Then test with:")
    print("  python examples/gcp_secrets_example.py")


def example_environment_vars():
    """Example 5: Secret resolution from environment variables."""
    print("\n=== Example 5: Environment Variable Secrets ===")

    print("\nEnvironment variables can also use secret syntax:")
    print()
    print("  export DB_PASSWORD='secret:mangrove-prod-db:password'")
    print("  export ENVIRONMENT=prod")
    print("  python src/app.py")
    print()
    print("The config system will automatically resolve the secret.")


def main():
    """Run all examples."""
    print("=" * 70)
    print("GCP Secret Manager Integration Examples")
    print("=" * 70)

    # Check if GCP_PROJECT_ID is set
    project_id = os.environ.get("GCP_PROJECT_ID")
    if not project_id:
        print("\nWarning: GCP_PROJECT_ID not set")
        print("Set it with: export GCP_PROJECT_ID=your-project-id")
        print("\nContinuing with examples (some may fail)...\n")

    try:
        example_direct_access()
        example_resolve_syntax()
        example_config_integration()
        example_environment_vars()
        example_create_test_secret()

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 70)
    print("Examples complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
