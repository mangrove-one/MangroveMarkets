"""Configuration management for MangroveMarkets.

Follows the standard config pattern:
1. ENVIRONMENT or APP_ENV determines which config file to load (defaults to 'local')
2. configuration-keys.json defines required keys — all must be present
3. Config values starting with 'secret:' are resolved via GCP Secret Manager
4. ONE GCP secret per environment (mangrovemarkets-config-{env})
5. All config values are set as attributes via setattr()
"""
import json
import os
import sys
from typing import Optional

from .gcp_secret_utils import resolve_secret_value


class _Config:
    """Singleton configuration loaded from environment-specific config files.

    All configuration keys defined in configuration-keys.json are set as
    instance attributes via setattr(). Access them directly:
        app_config.DB_HOST, app_config.XRPL_NETWORK, etc.
    """
    _instance: Optional["_Config"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._raw_config = {}
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.load_configuration()

    def load_configuration(self) -> None:
        """Load and validate configuration from environment-specific JSON file."""
        environment = os.getenv("ENVIRONMENT") or os.getenv("APP_ENV")
        if not environment:
            environment = "local"
            print(f"ENVIRONMENT/APP_ENV not set — defaulting to '{environment}'")
        setattr(self, "ENVIRONMENT", environment)

        configuration_keys = self.get_configuration_keys()
        self.load_config_file()
        gcp_project_id = os.getenv("GCP_PROJECT_ID")
        if not gcp_project_id:
            print("GCP_PROJECT_ID not set. Secret Manager lookups will fail.")

        for key in configuration_keys:
            if key not in self._raw_config:
                print(f"Configuration key {key} missing from config file.")
                sys.exit(1)
            key_value = self.get_key_value(key)
            if str(key_value).strip().lower() in {"none", "null"}:
                key_value = None
            setattr(self, key, key_value)

    @staticmethod
    def get_configuration_keys() -> set:
        """Load required configuration keys from configuration-keys.json."""
        try:
            config_dir = os.path.dirname(os.path.abspath(__file__))
            keys_path = os.path.join(config_dir, "config", "configuration-keys.json")
            with open(keys_path, "r") as f:
                keys_list = json.load(f)
                return set(keys_list["required_keys"])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Failed to load configuration-keys.json: {e}")
            sys.exit(1)

    def load_config_file(self) -> None:
        """Load the environment-specific config JSON file."""
        filename = f"config/{self.ENVIRONMENT}-config.json"
        try:
            config_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(config_dir, filename)

            if not os.path.exists(file_path):
                print(f"Config file not found: {file_path}")
                sys.exit(1)

            with open(file_path, "r") as f:
                config_data = json.load(f)

            self._raw_config.update(config_data)

        except Exception as e:
            print(f"Error loading {filename}: {e}")
            sys.exit(1)

    def get_key_value(self, key: str) -> object:
        """Resolve a config value, fetching from GCP Secret Manager if needed.

        Values starting with 'secret:' use format 'secret:<secret-name>:<property>'
        and are resolved via GCP Secret Manager.

        Args:
            key: The configuration key to resolve.

        Returns:
            The resolved configuration value.
        """
        value = self._raw_config.get(key)
        str_val = str(value)
        if str_val.startswith("secret:"):
            # resolve_secret_value handles the secret:name:property parsing
            value = resolve_secret_value(str_val)
        return value

    @classmethod
    def reset(cls) -> None:
        """Reset singleton for testing."""
        cls._instance = None


# Module-level singleton. Loaded once at import time.
app_config = _Config()
