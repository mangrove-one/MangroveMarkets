"""Tests for Config class with GCP Secret Manager integration."""
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.shared.config import Config
from src.shared.gcp_secret_utils import reset_secret_manager


@pytest.fixture(autouse=True)
def reset_config():
    """Reset config singleton before each test."""
    Config.reset()
    reset_secret_manager()
    yield
    Config.reset()
    reset_secret_manager()


@pytest.fixture
def temp_config_dir(tmp_path, monkeypatch):
    """Create temporary config directory."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    # Patch the config directory location
    original_file = Path(__file__).parent.parent.parent / "src" / "shared" / "config.py"

    def mock_load(self):
        self._environment = os.environ.get("ENVIRONMENT") or os.environ.get("APP_ENV")
        if not self._environment:
            self._environment = "local"

        config_file = config_dir / f"{self._environment}-config.json"

        if config_file.exists():
            with open(config_file) as f:
                self._raw_config = json.load(f)

        # Resolve secrets in config values
        self._raw_config = self._resolve_secrets(self._raw_config)

    monkeypatch.setattr(Config, "_load", mock_load)

    return config_dir


class TestConfigSecretResolution:
    """Tests for Config with secret resolution."""

    def test_config_without_secrets(self, temp_config_dir):
        """Test config loading without any secrets."""
        config_data = {
            "DB_HOST": "localhost",
            "DB_PASSWORD": "plain-password"
        }

        config_file = temp_config_dir / "test-config.json"
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        os.environ["ENVIRONMENT"] = "test"
        config = Config.get()

        assert config.DB_HOST == "localhost"
        assert config.DB_PASSWORD == "plain-password"

    @patch("src.shared.config.resolve_secret_value")
    def test_config_with_secrets(self, mock_resolve, temp_config_dir):
        """Test config loading with secret references."""
        # Setup mock
        def resolve_side_effect(value):
            if value == "secret:db-creds:password":
                return "resolved-secret-password"
            return value

        mock_resolve.side_effect = resolve_side_effect

        config_data = {
            "DB_HOST": "localhost",
            "DB_PASSWORD": "secret:db-creds:password"
        }

        config_file = temp_config_dir / "prod-config.json"
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        os.environ["ENVIRONMENT"] = "prod"
        config = Config.get()

        assert config.DB_HOST == "localhost"
        assert config.DB_PASSWORD == "resolved-secret-password"
        assert mock_resolve.call_count >= 1

    @patch("src.shared.config.resolve_secret_value")
    def test_config_secret_failure_fallback(self, mock_resolve, temp_config_dir, capsys):
        """Test that config continues with original value if secret resolution fails."""
        # Setup mock to raise exception
        def resolve_side_effect(value):
            if value.startswith("secret:"):
                raise ValueError("Secret not found")
            return value

        mock_resolve.side_effect = resolve_side_effect

        config_data = {
            "DB_HOST": "localhost",
            "DB_PASSWORD": "secret:db-creds:password"
        }

        config_file = temp_config_dir / "prod-config.json"
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        os.environ["ENVIRONMENT"] = "prod"
        config = Config.get()

        # Should fall back to original value
        assert config.DB_PASSWORD == "secret:db-creds:password"

        # Should have printed warning
        captured = capsys.readouterr()
        assert "Warning: Failed to resolve secret" in captured.err

    @patch("src.shared.config.resolve_secret_value")
    def test_env_var_secret_resolution(self, mock_resolve, temp_config_dir, monkeypatch):
        """Test secret resolution for environment variables."""
        # Setup mock
        def resolve_side_effect(value):
            if value == "secret:jwt:token":
                return "resolved-jwt-secret"
            return value

        mock_resolve.side_effect = resolve_side_effect

        # Create config without JWT_SECRET
        config_data = {"DB_HOST": "localhost"}
        config_file = temp_config_dir / "test-config.json"
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        # Set environment variable with secret reference
        monkeypatch.setenv("ENVIRONMENT", "test")
        monkeypatch.setenv("JWT_SECRET", "secret:jwt:token")

        config = Config.get()

        # Should resolve the secret from env var
        assert config.JWT_SECRET == "resolved-jwt-secret"

    def test_nested_config_secrets(self, temp_config_dir):
        """Test that nested dictionaries are handled (if implemented)."""
        config_data = {
            "database": {
                "host": "localhost",
                "credentials": {
                    "password": "secret:db:password"
                }
            }
        }

        config_file = temp_config_dir / "test-config.json"
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        os.environ["ENVIRONMENT"] = "test"

        # This test documents current behavior
        # Nested secrets would be resolved by _resolve_secrets recursion
        config = Config.get()
        assert "database" in config._raw_config


class TestConfigGetValue:
    """Tests for the _get_value helper method."""

    @patch("src.shared.config.resolve_secret_value")
    def test_get_value_from_config(self, mock_resolve, temp_config_dir):
        """Test _get_value prefers config file over env."""
        config_data = {"TEST_KEY": "config-value"}
        config_file = temp_config_dir / "test-config.json"
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        os.environ["ENVIRONMENT"] = "test"
        os.environ["TEST_KEY"] = "env-value"

        config = Config.get()

        # Config file should win (already resolved)
        # We can't directly test _get_value, but we can verify behavior
        assert config._raw_config["TEST_KEY"] == "config-value"

    @patch("src.shared.config.resolve_secret_value")
    def test_get_value_from_env(self, mock_resolve, temp_config_dir, monkeypatch):
        """Test _get_value falls back to env."""

        def resolve_side_effect(value):
            if value == "secret:test:key":
                return "resolved-from-env"
            return value

        mock_resolve.side_effect = resolve_side_effect

        # Empty config
        config_data = {}
        config_file = temp_config_dir / "test-config.json"
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        monkeypatch.setenv("ENVIRONMENT", "test")
        monkeypatch.setenv("JWT_SECRET", "secret:test:key")

        config = Config.get()

        # Should resolve from env var
        assert config.JWT_SECRET == "resolved-from-env"

    def test_get_value_default(self, temp_config_dir):
        """Test _get_value uses default when not in config or env."""
        # Empty config
        config_data = {}
        config_file = temp_config_dir / "test-config.json"
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        os.environ["ENVIRONMENT"] = "test"

        config = Config.get()

        # Should use default
        assert config.JWT_SECRET == "dev-secret-change-me"


class TestConfigIntegration:
    """Integration tests with realistic scenarios."""

    @patch("src.shared.gcp_secret_utils.secretmanager.SecretManagerServiceClient")
    def test_full_prod_config_flow(self, mock_client, temp_config_dir, monkeypatch):
        """Test loading production config with real secret resolution."""
        monkeypatch.setenv("GCP_PROJECT_ID", "test-project")
        monkeypatch.setenv("ENVIRONMENT", "prod")

        # Mock GCP response
        secret_data = {
            "host": "prod-db.example.com",
            "username": "prod_user",
            "password": "super-secret-password",
            "database": "mangrove_prod"
        }
        mock_response = MagicMock()
        mock_response.payload.data.decode.return_value = json.dumps(secret_data)

        mock_client_instance = mock_client.return_value
        mock_client_instance.access_secret_version.return_value = mock_response

        # Create prod config with secrets
        config_data = {
            "ENVIRONMENT": "prod",
            "DB_HOST": "secret:mangrove-prod-db:host",
            "DB_USER": "secret:mangrove-prod-db:username",
            "DB_PASSWORD": "secret:mangrove-prod-db:password",
            "DB_NAME": "secret:mangrove-prod-db:database",
            "JWT_SECRET": "dev-secret-change-me",  # Will use default
            "AUTH_ENABLED": True
        }

        config_file = temp_config_dir / "prod-config.json"
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        # Load config
        config = Config.get()

        # Verify secrets were resolved
        assert config.DB_HOST == "prod-db.example.com"
        assert config.DB_USER == "prod_user"
        assert config.DB_PASSWORD == "super-secret-password"
        assert config.DB_NAME == "mangrove_prod"
        assert config.AUTH_ENABLED is True

        # Verify caching - should only fetch secret once
        assert mock_client_instance.access_secret_version.call_count == 1
