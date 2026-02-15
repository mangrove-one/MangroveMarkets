"""GCP Secret Manager utilities for MangroveMarkets.

This module provides utilities for fetching secrets from Google Cloud Platform Secret Manager.
Supports the secret:<name>:<property> syntax for referencing secrets in configuration.
"""
import json
import os
from typing import Any, Optional

try:
    from google.cloud import secretmanager
    from google.api_core import exceptions as gcp_exceptions
    HAS_GCP = True
except ImportError:
    HAS_GCP = False


class GCPSecretManager:
    """Client for fetching secrets from GCP Secret Manager."""

    def __init__(self, project_id: Optional[str] = None):
        """Initialize GCP Secret Manager client.

        Args:
            project_id: GCP project ID. If None, uses GCP_PROJECT_ID env var.
        """
        if not HAS_GCP:
            raise ImportError(
                "google-cloud-secret-manager is not installed. "
                "Install it with: pip install google-cloud-secret-manager"
            )

        self.project_id = project_id or os.environ.get("GCP_PROJECT_ID")
        if not self.project_id:
            raise ValueError(
                "GCP project ID not provided. Set GCP_PROJECT_ID environment variable "
                "or pass project_id to GCPSecretManager constructor."
            )

        self.client = secretmanager.SecretManagerServiceClient()
        self._cache: dict[str, dict[str, Any]] = {}

    def get_secret(self, secret_name: str, version: str = "latest") -> str:
        """Fetch a secret from GCP Secret Manager.

        Args:
            secret_name: Name of the secret
            version: Version of the secret (default: "latest")

        Returns:
            Secret value as string

        Raises:
            ValueError: If secret cannot be fetched
        """
        # Check cache first
        cache_key = f"{secret_name}:{version}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            name = f"projects/{self.project_id}/secrets/{secret_name}/versions/{version}"
            response = self.client.access_secret_version(request={"name": name})
            secret_value = response.payload.data.decode("UTF-8")

            # Cache the result
            self._cache[cache_key] = secret_value
            return secret_value

        except gcp_exceptions.NotFound:
            raise ValueError(
                f"Secret '{secret_name}' not found in project '{self.project_id}'"
            )
        except gcp_exceptions.PermissionDenied:
            raise ValueError(
                f"Permission denied accessing secret '{secret_name}'. "
                "Ensure service account has roles/secretmanager.secretAccessor"
            )
        except Exception as e:
            raise ValueError(
                f"Error fetching secret '{secret_name}': {e}"
            )

    def get_secret_json(self, secret_name: str, version: str = "latest") -> dict[str, Any]:
        """Fetch a JSON secret from GCP Secret Manager.

        Args:
            secret_name: Name of the secret
            version: Version of the secret (default: "latest")

        Returns:
            Parsed JSON as dictionary

        Raises:
            ValueError: If secret cannot be fetched or is not valid JSON
        """
        secret_value = self.get_secret(secret_name, version)
        try:
            return json.loads(secret_value)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Secret '{secret_name}' is not valid JSON: {e}"
            )

    def get_secret_property(
        self,
        secret_name: str,
        property_name: str,
        version: str = "latest"
    ) -> Any:
        """Fetch a specific property from a JSON secret.

        Args:
            secret_name: Name of the secret
            property_name: Property to extract from the JSON
            version: Version of the secret (default: "latest")

        Returns:
            Value of the specified property

        Raises:
            ValueError: If secret cannot be fetched or property doesn't exist
        """
        secret_json = self.get_secret_json(secret_name, version)

        if property_name not in secret_json:
            raise ValueError(
                f"Property '{property_name}' not found in secret '{secret_name}'. "
                f"Available properties: {list(secret_json.keys())}"
            )

        return secret_json[property_name]

    def clear_cache(self) -> None:
        """Clear the secret cache."""
        self._cache.clear()


# Global instance (lazy-initialized)
_secret_manager: Optional[GCPSecretManager] = None


def get_secret_manager() -> GCPSecretManager:
    """Get or create the global GCPSecretManager instance.

    Returns:
        GCPSecretManager instance
    """
    global _secret_manager
    if _secret_manager is None:
        _secret_manager = GCPSecretManager()
    return _secret_manager


def resolve_secret_value(value: str) -> Any:
    """Resolve a secret value if it uses the secret:<name>:<property> syntax.

    Supports these formats:
    - "secret:<name>" - Returns entire secret as string
    - "secret:<name>:<property>" - Returns specific property from JSON secret
    - "secret:<name>::<version>" - Returns entire secret with specific version
    - "secret:<name>:<property>:<version>" - Returns property with specific version

    Args:
        value: Configuration value (may or may not be a secret reference)

    Returns:
        Resolved value (secret or original value)

    Raises:
        ValueError: If secret reference is invalid or cannot be fetched
    """
    if not isinstance(value, str) or not value.startswith("secret:"):
        return value

    parts = value.split(":")
    if len(parts) < 2:
        raise ValueError(
            f"Invalid secret reference '{value}'. "
            "Expected format: secret:<name> or secret:<name>:<property>"
        )

    secret_name = parts[1]
    property_name = None
    version = "latest"

    # Parse the format
    if len(parts) == 2:
        # secret:<name>
        pass
    elif len(parts) == 3:
        # Could be secret:<name>:<property> or secret:<name>::<version>
        if parts[2]:
            property_name = parts[2]
        else:
            # Empty property means just version (secret:<name>::<version> not supported yet)
            pass
    elif len(parts) == 4:
        # secret:<name>:<property>:<version>
        property_name = parts[2] if parts[2] else None
        version = parts[3] if parts[3] else "latest"

    manager = get_secret_manager()

    if property_name:
        return manager.get_secret_property(secret_name, property_name, version)
    else:
        return manager.get_secret(secret_name, version)


def reset_secret_manager() -> None:
    """Reset the global secret manager instance (for testing)."""
    global _secret_manager
    if _secret_manager is not None:
        _secret_manager.clear_cache()
    _secret_manager = None
