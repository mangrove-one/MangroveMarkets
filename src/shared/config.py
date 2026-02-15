"""Configuration management for MangroveMarkets."""
import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

from .gcp_secret_utils import resolve_secret_value


class Config:
    """Singleton configuration loaded from environment and config files."""
    _instance: Optional["Config"] = None

    def __init__(self):
        self._raw_config: dict = {}
        self._environment: Optional[str] = None

    @classmethod
    def get(cls) -> "Config":
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._load()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset singleton for testing."""
        cls._instance = None

    def _load(self) -> None:
        self._environment = os.environ.get("ENVIRONMENT") or os.environ.get("APP_ENV")
        if not self._environment:
            self._environment = "local"

        config_dir = Path(__file__).parent / "config"
        config_file = config_dir / f"{self._environment}-config.json"

        if config_file.exists():
            with open(config_file) as f:
                self._raw_config = json.load(f)

        # Resolve secrets in config values
        self._raw_config = self._resolve_secrets(self._raw_config)

    def _resolve_secrets(self, config_dict: dict[str, Any]) -> dict[str, Any]:
        """Recursively resolve secret references in config values.

        Args:
            config_dict: Configuration dictionary potentially containing secret references

        Returns:
            Dictionary with resolved secret values
        """
        resolved = {}
        for key, value in config_dict.items():
            if isinstance(value, dict):
                resolved[key] = self._resolve_secrets(value)
            elif isinstance(value, str):
                try:
                    resolved[key] = resolve_secret_value(value)
                except Exception as e:
                    # Log warning but don't fail - allow fallback to env vars
                    print(f"Warning: Failed to resolve secret for {key}: {e}", file=sys.stderr)
                    resolved[key] = value
            else:
                resolved[key] = value
        return resolved

    def _get_value(self, key: str, env_var: str, default: Any) -> Any:
        """Get config value with secret resolution support.

        Checks in order:
        1. Resolved config file value
        2. Environment variable (with secret resolution)
        3. Default value

        Args:
            key: Config file key
            env_var: Environment variable name
            default: Default value if not found

        Returns:
            Configuration value
        """
        # First check config file (already resolved)
        if key in self._raw_config:
            return self._raw_config[key]

        # Then check environment variable (needs resolution)
        env_value = os.environ.get(env_var)
        if env_value is not None:
            try:
                return resolve_secret_value(env_value)
            except Exception as e:
                print(f"Warning: Failed to resolve secret from {env_var}: {e}", file=sys.stderr)
                return env_value

        return default

    @property
    def ENVIRONMENT(self) -> str:
        return self._environment or "local"

    @property
    def XRPL_NETWORK(self) -> str:
        return self._get_value("XRPL_NETWORK", "XRPL_NETWORK", "testnet")

    @property
    def XRPL_NODE_URL(self) -> str:
        defaults = {
            "testnet": "https://s.altnet.rippletest.net:51234",
            "devnet": "https://s.devnet.rippletest.net:51234",
            "mainnet": "https://xrplcluster.com",
        }
        return self._get_value("XRPL_NODE_URL", "XRPL_NODE_URL", defaults.get(self.XRPL_NETWORK, defaults["testnet"]))

    @property
    def MCP_HOST(self) -> str:
        return self._get_value("MCP_HOST", "MCP_HOST", "0.0.0.0")

    @property
    def MCP_PORT(self) -> int:
        return int(self._get_value("MCP_PORT", "MCP_PORT", "8080"))

    @property
    def DB_HOST(self) -> str:
        return self._get_value("DB_HOST", "DB_HOST", "localhost")

    @property
    def DB_PORT(self) -> int:
        return int(self._get_value("DB_PORT", "DB_PORT", "5432"))

    @property
    def DB_NAME(self) -> str:
        return self._get_value("DB_NAME", "DB_NAME", "mangrove_db")

    @property
    def DB_USER(self) -> str:
        return self._get_value("DB_USER", "DB_USER", "postgres")

    @property
    def DB_PASSWORD(self) -> str:
        return self._get_value("DB_PASSWORD", "DB_PASSWORD", "postgres")

    @property
    def JWT_SECRET(self) -> str:
        return self._get_value("JWT_SECRET", "JWT_SECRET", "dev-secret-change-me")

    @property
    def AUTH_ENABLED(self) -> bool:
        val = self._get_value("AUTH_ENABLED", "AUTH_ENABLED", "false")
        return str(val).lower() in ("true", "1", "yes")

    @property
    def MARKETPLACE_FEE_PERCENT(self) -> float:
        return float(self._get_value("MARKETPLACE_FEE_PERCENT", "MARKETPLACE_FEE_PERCENT", "1.0"))

    @property
    def DEX_FEE_PERCENT(self) -> float:
        return float(self._get_value("DEX_FEE_PERCENT", "DEX_FEE_PERCENT", "0.05"))


config = Config.get()
