"""Tests for _Config class -- validates the template-based configuration pattern.

Covers:
- ENVIRONMENT defaults to 'local' if not set
- All required keys from configuration-keys.json must be present in config file
- secret:name:property values are resolved via resolve_secret_value
- None/null string values become Python None
- Configuration-keys.json file integrity
"""
import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from src.shared.config import _Config


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "shared" / "config"
KEYS_FILE = CONFIG_DIR / "configuration-keys.json"


def _load_required_keys() -> set:
    with open(KEYS_FILE) as f:
        return set(json.load(f)["required_keys"])


def _build_complete_config(overrides: dict | None = None) -> dict:
    """Return a config dict that satisfies all required keys with test defaults."""
    base = {
        "DB_HOST": "localhost",
        "DB_NAME": "test_db",
        "DB_USER": "test_user",
        "DB_PASSWORD": "test_pass",
        "DB_PORT": 5432,
        "DB_SSLMODE": "disable",
        "CLOUD_SQL_CONNECTION_NAME": "null",
        "JWT_SECRET": "test-jwt-secret",
        "AUTH_ENABLED": False,
        "XRPL_NETWORK": "testnet",
        "XRPL_NODE_URL": "https://s.altnet.rippletest.net:51234",
        "MCP_HOST": "127.0.0.1",
        "MCP_PORT": 8081,
        "MARKETPLACE_FEE_PERCENT": 0.0,
        "DEX_FEE_PERCENT": 0.0,
    }
    if overrides:
        base.update(overrides)
    return base


def _setup_tmp_config(monkeypatch, tmp_path, env_name, config_data):
    """Set up a temp directory with config files and patch _Config to read from it.

    Patches os.path.abspath and os.path.dirname so _Config resolves its
    config/ subdirectory from tmp_path instead of the real source tree.
    """
    config_dir = tmp_path / "config"
    config_dir.mkdir(exist_ok=True)

    # Copy configuration-keys.json into temp config dir
    keys_dest = config_dir / "configuration-keys.json"
    keys_dest.write_text(KEYS_FILE.read_text())

    # Write environment config file
    config_file = config_dir / f"{env_name}-config.json"
    config_file.write_text(json.dumps(config_data))

    monkeypatch.setenv("ENVIRONMENT", env_name)
    monkeypatch.setenv("GCP_PROJECT_ID", "test-project")

    # Redirect _Config's path resolution to our temp directory
    original_abspath = os.path.abspath
    original_dirname = os.path.dirname

    def patched_abspath(path):
        if "config.py" in str(path):
            return str(tmp_path / "config.py")
        return original_abspath(path)

    def patched_dirname(path):
        if str(tmp_path) in str(path) and "config.py" in str(path):
            return str(tmp_path)
        return original_dirname(path)

    monkeypatch.setattr(os.path, "abspath", patched_abspath)
    monkeypatch.setattr(os.path, "dirname", patched_dirname)


# ---------------------------------------------------------------------------
# Tests: ENVIRONMENT default behavior
# ---------------------------------------------------------------------------

class TestEnvironmentDefault:
    """Config defaults to 'local' if ENVIRONMENT / APP_ENV is not set."""

    def test_defaults_to_local_when_environment_not_set(self, monkeypatch, tmp_path):
        """When ENVIRONMENT/APP_ENV are not set, config defaults to 'local'."""
        _setup_tmp_config(monkeypatch, tmp_path, "local", _build_complete_config())
        # Remove env vars *after* _setup_tmp_config so path patching is in place
        # but _Config sees neither ENVIRONMENT nor APP_ENV
        monkeypatch.delenv("ENVIRONMENT", raising=False)
        monkeypatch.delenv("APP_ENV", raising=False)

        with patch("src.shared.config.resolve_secret_value", side_effect=lambda v: v):
            instance = _Config()
            assert instance.ENVIRONMENT == "local"

    def test_accepts_environment_var(self, monkeypatch, tmp_path):
        """ENVIRONMENT env var is accepted."""
        _setup_tmp_config(monkeypatch, tmp_path, "test", _build_complete_config())

        with patch("src.shared.config.resolve_secret_value", side_effect=lambda v: v):
            instance = _Config()
            assert instance.ENVIRONMENT == "test"

    def test_accepts_app_env_var(self, monkeypatch, tmp_path):
        """APP_ENV is an acceptable alternative to ENVIRONMENT."""
        config_data = _build_complete_config()
        config_dir = tmp_path / "config"
        config_dir.mkdir(exist_ok=True)
        keys_dest = config_dir / "configuration-keys.json"
        keys_dest.write_text(KEYS_FILE.read_text())
        config_file = config_dir / "myenv-config.json"
        config_file.write_text(json.dumps(config_data))

        monkeypatch.delenv("ENVIRONMENT", raising=False)
        monkeypatch.setenv("APP_ENV", "myenv")
        monkeypatch.setenv("GCP_PROJECT_ID", "test-project")

        original_abspath = os.path.abspath
        original_dirname = os.path.dirname

        def patched_abspath(path):
            if "config.py" in str(path):
                return str(tmp_path / "config.py")
            return original_abspath(path)

        def patched_dirname(path):
            if str(tmp_path) in str(path) and "config.py" in str(path):
                return str(tmp_path)
            return original_dirname(path)

        monkeypatch.setattr(os.path, "abspath", patched_abspath)
        monkeypatch.setattr(os.path, "dirname", patched_dirname)

        with patch("src.shared.config.resolve_secret_value", side_effect=lambda v: v):
            instance = _Config()
            assert instance.ENVIRONMENT == "myenv"


# ---------------------------------------------------------------------------
# Tests: Required keys validation
# ---------------------------------------------------------------------------

class TestRequiredKeys:
    """Config must exit if any required key is missing from the config file."""

    def test_exits_when_required_key_missing(self, monkeypatch, tmp_path):
        incomplete_config = _build_complete_config()
        del incomplete_config["DB_HOST"]

        _setup_tmp_config(monkeypatch, tmp_path, "test", incomplete_config)

        with pytest.raises(SystemExit):
            _Config()

    def test_exits_when_multiple_keys_missing(self, monkeypatch, tmp_path):
        incomplete_config = _build_complete_config()
        del incomplete_config["DB_HOST"]
        del incomplete_config["JWT_SECRET"]

        _setup_tmp_config(monkeypatch, tmp_path, "test", incomplete_config)

        with pytest.raises(SystemExit):
            _Config()

    def test_succeeds_with_all_required_keys(self, monkeypatch, tmp_path):
        _setup_tmp_config(monkeypatch, tmp_path, "test", _build_complete_config())

        with patch("src.shared.config.resolve_secret_value", side_effect=lambda v: v):
            instance = _Config()
            assert instance.DB_HOST == "localhost"

    def test_all_real_config_files_have_required_keys(self):
        """Every environment config JSON in the source tree must have all required keys."""
        required = _load_required_keys()
        for config_file in CONFIG_DIR.glob("*-config.json"):
            with open(config_file) as f:
                data = json.load(f)
            missing = required - set(data.keys())
            assert not missing, (
                f"{config_file.name} is missing required keys: {missing}"
            )


# ---------------------------------------------------------------------------
# Tests: Secret resolution
# ---------------------------------------------------------------------------

class TestSecretResolution:
    """Values starting with 'secret:' are resolved via resolve_secret_value."""

    def test_secret_values_are_resolved(self, monkeypatch, tmp_path):
        config_data = _build_complete_config({
            "DB_PASSWORD": "secret:mangrovemarkets-config-test:DB_PASSWORD",
        })

        _setup_tmp_config(monkeypatch, tmp_path, "test", config_data)

        def mock_resolve(value):
            if value == "secret:mangrovemarkets-config-test:DB_PASSWORD":
                return "resolved-password-from-gcp"
            return value

        with patch("src.shared.config.resolve_secret_value", side_effect=mock_resolve):
            instance = _Config()
            assert instance.DB_PASSWORD == "resolved-password-from-gcp"

    def test_non_secret_values_pass_through(self, monkeypatch, tmp_path):
        _setup_tmp_config(monkeypatch, tmp_path, "test", _build_complete_config())

        with patch("src.shared.config.resolve_secret_value", side_effect=lambda v: v):
            instance = _Config()
            assert instance.DB_HOST == "localhost"
            assert instance.DB_NAME == "test_db"
            assert instance.XRPL_NETWORK == "testnet"

    def test_multiple_secrets_resolved(self, monkeypatch, tmp_path):
        config_data = _build_complete_config({
            "DB_PASSWORD": "secret:mangrovemarkets-config-test:DB_PASSWORD",
            "JWT_SECRET": "secret:mangrovemarkets-config-test:JWT_SECRET",
        })

        _setup_tmp_config(monkeypatch, tmp_path, "test", config_data)

        resolved_map = {
            "secret:mangrovemarkets-config-test:DB_PASSWORD": "db-pass-resolved",
            "secret:mangrovemarkets-config-test:JWT_SECRET": "jwt-resolved",
        }

        def mock_resolve(value):
            return resolved_map.get(value, value)

        with patch("src.shared.config.resolve_secret_value", side_effect=mock_resolve):
            instance = _Config()
            assert instance.DB_PASSWORD == "db-pass-resolved"
            assert instance.JWT_SECRET == "jwt-resolved"


# ---------------------------------------------------------------------------
# Tests: None/null handling
# ---------------------------------------------------------------------------

class TestNoneNullHandling:
    """String values 'None' and 'null' should become Python None."""

    def test_null_string_becomes_none(self, monkeypatch, tmp_path):
        config_data = _build_complete_config({
            "CLOUD_SQL_CONNECTION_NAME": "null",
        })

        _setup_tmp_config(monkeypatch, tmp_path, "test", config_data)

        with patch("src.shared.config.resolve_secret_value", side_effect=lambda v: v):
            instance = _Config()
            assert instance.CLOUD_SQL_CONNECTION_NAME is None

    def test_none_string_becomes_none(self, monkeypatch, tmp_path):
        config_data = _build_complete_config({
            "CLOUD_SQL_CONNECTION_NAME": "None",
        })

        _setup_tmp_config(monkeypatch, tmp_path, "test", config_data)

        with patch("src.shared.config.resolve_secret_value", side_effect=lambda v: v):
            instance = _Config()
            assert instance.CLOUD_SQL_CONNECTION_NAME is None

    def test_json_null_becomes_none(self, monkeypatch, tmp_path):
        """JSON null becomes Python None, and str(None) == 'None' triggers conversion."""
        config_data = _build_complete_config({
            "CLOUD_SQL_CONNECTION_NAME": None,
        })

        _setup_tmp_config(monkeypatch, tmp_path, "test", config_data)

        with patch("src.shared.config.resolve_secret_value", side_effect=lambda v: v):
            instance = _Config()
            assert instance.CLOUD_SQL_CONNECTION_NAME is None

    def test_real_values_not_converted_to_none(self, monkeypatch, tmp_path):
        config_data = _build_complete_config({
            "DB_HOST": "my-real-host",
        })

        _setup_tmp_config(monkeypatch, tmp_path, "test", config_data)

        with patch("src.shared.config.resolve_secret_value", side_effect=lambda v: v):
            instance = _Config()
            assert instance.DB_HOST == "my-real-host"


# ---------------------------------------------------------------------------
# Tests: Config file missing
# ---------------------------------------------------------------------------

class TestConfigFileMissing:
    """Config must exit if the environment config file does not exist."""

    def test_exits_when_config_file_not_found(self, monkeypatch, tmp_path):
        # Set up keys file but NO config JSON for the environment
        config_dir = tmp_path / "config"
        config_dir.mkdir(exist_ok=True)
        keys_dest = config_dir / "configuration-keys.json"
        keys_dest.write_text(KEYS_FILE.read_text())

        monkeypatch.setenv("ENVIRONMENT", "nonexistent")
        monkeypatch.setenv("GCP_PROJECT_ID", "test-project")

        original_abspath = os.path.abspath
        original_dirname = os.path.dirname

        def patched_abspath(path):
            if "config.py" in str(path):
                return str(tmp_path / "config.py")
            return original_abspath(path)

        def patched_dirname(path):
            if str(tmp_path) in str(path) and "config.py" in str(path):
                return str(tmp_path)
            return original_dirname(path)

        monkeypatch.setattr(os.path, "abspath", patched_abspath)
        monkeypatch.setattr(os.path, "dirname", patched_dirname)

        with pytest.raises(SystemExit):
            _Config()


# ---------------------------------------------------------------------------
# Tests: Setattr-based attribute access
# ---------------------------------------------------------------------------

class TestSetattrAttributes:
    """All config values are set as instance attributes via setattr()."""

    def test_all_required_keys_become_attributes(self, monkeypatch, tmp_path):
        config_data = _build_complete_config()
        _setup_tmp_config(monkeypatch, tmp_path, "test", config_data)

        with patch("src.shared.config.resolve_secret_value", side_effect=lambda v: v):
            instance = _Config()

        required = _load_required_keys()
        for key in required:
            assert hasattr(instance, key), f"Config should have attribute {key}"

    def test_environment_is_set_as_attribute(self, monkeypatch, tmp_path):
        _setup_tmp_config(monkeypatch, tmp_path, "test", _build_complete_config())

        with patch("src.shared.config.resolve_secret_value", side_effect=lambda v: v):
            instance = _Config()
            assert instance.ENVIRONMENT == "test"


# ---------------------------------------------------------------------------
# Tests: configuration-keys.json integrity
# ---------------------------------------------------------------------------

class TestConfigurationKeysFile:
    """Validate the configuration-keys.json file itself."""

    def test_keys_file_exists(self):
        assert KEYS_FILE.exists(), "configuration-keys.json must exist"

    def test_keys_file_is_valid_json(self):
        with open(KEYS_FILE) as f:
            data = json.load(f)
        assert "required_keys" in data
        assert isinstance(data["required_keys"], list)
        assert len(data["required_keys"]) > 0

    def test_no_duplicate_keys(self):
        with open(KEYS_FILE) as f:
            data = json.load(f)
        keys = data["required_keys"]
        assert len(keys) == len(set(keys)), "Duplicate keys in configuration-keys.json"


# ---------------------------------------------------------------------------
# Tests: Reset for testing
# ---------------------------------------------------------------------------

class TestReset:
    """The reset() classmethod clears the singleton for testing."""

    def test_reset_clears_singleton(self):
        _Config.reset()
        assert _Config._instance is None
