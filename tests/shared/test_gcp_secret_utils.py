"""Tests for GCP Secret Manager utilities."""
import json
import os
import pytest
from unittest.mock import MagicMock, patch

from src.shared.gcp_secret_utils import (
    GCPSecretManager,
    resolve_secret_value,
    reset_secret_manager,
)


@pytest.fixture
def mock_secret_manager_client():
    """Mock GCP Secret Manager client."""
    with patch("src.shared.gcp_secret_utils.secretmanager.SecretManagerServiceClient") as mock_client:
        yield mock_client


@pytest.fixture
def mock_project_id(monkeypatch):
    """Set GCP_PROJECT_ID for tests."""
    monkeypatch.setenv("GCP_PROJECT_ID", "test-project")
    yield
    reset_secret_manager()


class TestGCPSecretManager:
    """Tests for GCPSecretManager class."""

    def test_init_with_project_id(self, mock_secret_manager_client):
        """Test initialization with explicit project ID."""
        manager = GCPSecretManager(project_id="my-project")
        assert manager.project_id == "my-project"

    def test_init_from_env(self, mock_secret_manager_client, mock_project_id):
        """Test initialization from environment variable."""
        manager = GCPSecretManager()
        assert manager.project_id == "test-project"

    def test_init_without_project_id(self, mock_secret_manager_client, monkeypatch):
        """Test initialization fails without project ID."""
        monkeypatch.delenv("GCP_PROJECT_ID", raising=False)
        with pytest.raises(ValueError, match="GCP project ID not provided"):
            GCPSecretManager()

    def test_get_secret_success(self, mock_secret_manager_client, mock_project_id):
        """Test successful secret retrieval."""
        mock_response = MagicMock()
        mock_response.payload.data.decode.return_value = "secret-value"

        mock_client_instance = mock_secret_manager_client.return_value
        mock_client_instance.access_secret_version.return_value = mock_response

        manager = GCPSecretManager()
        result = manager.get_secret("my-secret")

        assert result == "secret-value"
        mock_client_instance.access_secret_version.assert_called_once()

    def test_get_secret_cached(self, mock_secret_manager_client, mock_project_id):
        """Test that secrets are cached."""
        mock_response = MagicMock()
        mock_response.payload.data.decode.return_value = "secret-value"

        mock_client_instance = mock_secret_manager_client.return_value
        mock_client_instance.access_secret_version.return_value = mock_response

        manager = GCPSecretManager()
        result1 = manager.get_secret("my-secret")
        result2 = manager.get_secret("my-secret")

        assert result1 == result2 == "secret-value"
        # Should only call API once due to caching
        assert mock_client_instance.access_secret_version.call_count == 1

    def test_get_secret_json(self, mock_secret_manager_client, mock_project_id):
        """Test JSON secret retrieval."""
        secret_data = {"key": "value", "number": 42}
        mock_response = MagicMock()
        mock_response.payload.data.decode.return_value = json.dumps(secret_data)

        mock_client_instance = mock_secret_manager_client.return_value
        mock_client_instance.access_secret_version.return_value = mock_response

        manager = GCPSecretManager()
        result = manager.get_secret_json("my-secret")

        assert result == secret_data

    def test_get_secret_json_invalid(self, mock_secret_manager_client, mock_project_id):
        """Test JSON secret with invalid JSON."""
        mock_response = MagicMock()
        mock_response.payload.data.decode.return_value = "not-valid-json"

        mock_client_instance = mock_secret_manager_client.return_value
        mock_client_instance.access_secret_version.return_value = mock_response

        manager = GCPSecretManager()
        with pytest.raises(ValueError, match="not valid JSON"):
            manager.get_secret_json("my-secret")

    def test_get_secret_property(self, mock_secret_manager_client, mock_project_id):
        """Test getting a specific property from JSON secret."""
        secret_data = {"username": "admin", "password": "secret123"}
        mock_response = MagicMock()
        mock_response.payload.data.decode.return_value = json.dumps(secret_data)

        mock_client_instance = mock_secret_manager_client.return_value
        mock_client_instance.access_secret_version.return_value = mock_response

        manager = GCPSecretManager()
        result = manager.get_secret_property("my-secret", "password")

        assert result == "secret123"

    def test_get_secret_property_missing(self, mock_secret_manager_client, mock_project_id):
        """Test getting a missing property from JSON secret."""
        secret_data = {"username": "admin"}
        mock_response = MagicMock()
        mock_response.payload.data.decode.return_value = json.dumps(secret_data)

        mock_client_instance = mock_secret_manager_client.return_value
        mock_client_instance.access_secret_version.return_value = mock_response

        manager = GCPSecretManager()
        with pytest.raises(ValueError, match="Property 'password' not found"):
            manager.get_secret_property("my-secret", "password")

    def test_clear_cache(self, mock_secret_manager_client, mock_project_id):
        """Test cache clearing."""
        mock_response = MagicMock()
        mock_response.payload.data.decode.return_value = "secret-value"

        mock_client_instance = mock_secret_manager_client.return_value
        mock_client_instance.access_secret_version.return_value = mock_response

        manager = GCPSecretManager()
        manager.get_secret("my-secret")
        manager.clear_cache()
        manager.get_secret("my-secret")

        # Should call API twice due to cache clear
        assert mock_client_instance.access_secret_version.call_count == 2


class TestResolveSecretValue:
    """Tests for resolve_secret_value function."""

    @patch("src.shared.gcp_secret_utils.get_secret_manager")
    def test_non_secret_value(self, mock_get_manager):
        """Test that non-secret values pass through unchanged."""
        assert resolve_secret_value("normal-value") == "normal-value"
        assert resolve_secret_value(123) == 123
        assert resolve_secret_value(None) is None
        mock_get_manager.assert_not_called()

    @patch("src.shared.gcp_secret_utils.get_secret_manager")
    def test_secret_entire_value(self, mock_get_manager):
        """Test secret:<name> format."""
        mock_manager = MagicMock()
        mock_manager.get_secret.return_value = "secret-value"
        mock_get_manager.return_value = mock_manager

        result = resolve_secret_value("secret:my-secret")

        assert result == "secret-value"
        mock_manager.get_secret.assert_called_once_with("my-secret", "latest")

    @patch("src.shared.gcp_secret_utils.get_secret_manager")
    def test_secret_with_property(self, mock_get_manager):
        """Test secret:<name>:<property> format."""
        mock_manager = MagicMock()
        mock_manager.get_secret_property.return_value = "property-value"
        mock_get_manager.return_value = mock_manager

        result = resolve_secret_value("secret:my-secret:password")

        assert result == "property-value"
        mock_manager.get_secret_property.assert_called_once_with("my-secret", "password", "latest")

    @patch("src.shared.gcp_secret_utils.get_secret_manager")
    def test_secret_with_property_and_version(self, mock_get_manager):
        """Test secret:<name>:<property>:<version> format."""
        mock_manager = MagicMock()
        mock_manager.get_secret_property.return_value = "property-value"
        mock_get_manager.return_value = mock_manager

        result = resolve_secret_value("secret:my-secret:password:5")

        assert result == "property-value"
        mock_manager.get_secret_property.assert_called_once_with("my-secret", "password", "5")

    def test_invalid_secret_format(self):
        """Test invalid secret reference format."""
        with pytest.raises(ValueError, match="Invalid secret reference"):
            resolve_secret_value("secret:")


class TestIntegration:
    """Integration tests with mocked GCP client."""

    @patch("src.shared.gcp_secret_utils.secretmanager.SecretManagerServiceClient")
    def test_full_flow(self, mock_client, monkeypatch):
        """Test full flow from config value to resolved secret."""
        monkeypatch.setenv("GCP_PROJECT_ID", "test-project")

        # Mock the secret response
        secret_data = {"host": "db.example.com", "password": "secret123"}
        mock_response = MagicMock()
        mock_response.payload.data.decode.return_value = json.dumps(secret_data)

        mock_client_instance = mock_client.return_value
        mock_client_instance.access_secret_version.return_value = mock_response

        # Reset to get clean state
        reset_secret_manager()

        # Resolve multiple properties from same secret
        host = resolve_secret_value("secret:db-credentials:host")
        password = resolve_secret_value("secret:db-credentials:password")

        assert host == "db.example.com"
        assert password == "secret123"

        # Should only fetch once due to caching
        assert mock_client_instance.access_secret_version.call_count == 1

        # Clean up
        reset_secret_manager()
