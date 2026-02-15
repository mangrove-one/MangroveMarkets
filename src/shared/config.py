"""Configuration management for MangroveMarkets."""
import json
import os
import sys
from pathlib import Path
from typing import Optional


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

    @property
    def ENVIRONMENT(self) -> str:
        return self._environment or "local"

    @property
    def XRPL_NETWORK(self) -> str:
        return self._raw_config.get("XRPL_NETWORK", os.environ.get("XRPL_NETWORK", "testnet"))

    @property
    def XRPL_NODE_URL(self) -> str:
        defaults = {
            "testnet": "https://s.altnet.rippletest.net:51234",
            "devnet": "https://s.devnet.rippletest.net:51234",
            "mainnet": "https://xrplcluster.com",
        }
        return self._raw_config.get("XRPL_NODE_URL", os.environ.get("XRPL_NODE_URL", defaults.get(self.XRPL_NETWORK, defaults["testnet"])))

    @property
    def MCP_HOST(self) -> str:
        return self._raw_config.get("MCP_HOST", os.environ.get("MCP_HOST", "0.0.0.0"))

    @property
    def MCP_PORT(self) -> int:
        return int(self._raw_config.get("MCP_PORT", os.environ.get("MCP_PORT", "8080")))

    @property
    def DB_HOST(self) -> str:
        return self._raw_config.get("DB_HOST", os.environ.get("DB_HOST", "localhost"))

    @property
    def DB_PORT(self) -> int:
        return int(self._raw_config.get("DB_PORT", os.environ.get("DB_PORT", "5432")))

    @property
    def DB_NAME(self) -> str:
        return self._raw_config.get("DB_NAME", os.environ.get("DB_NAME", "mangrove_db"))

    @property
    def DB_USER(self) -> str:
        return self._raw_config.get("DB_USER", os.environ.get("DB_USER", "postgres"))

    @property
    def DB_PASSWORD(self) -> str:
        return self._raw_config.get("DB_PASSWORD", os.environ.get("DB_PASSWORD", "postgres"))

    @property
    def JWT_SECRET(self) -> str:
        return self._raw_config.get("JWT_SECRET", os.environ.get("JWT_SECRET", "dev-secret-change-me"))

    @property
    def AUTH_ENABLED(self) -> bool:
        val = self._raw_config.get("AUTH_ENABLED", os.environ.get("AUTH_ENABLED", "false"))
        return str(val).lower() in ("true", "1", "yes")

    @property
    def MARKETPLACE_FEE_PERCENT(self) -> float:
        return float(self._raw_config.get("MARKETPLACE_FEE_PERCENT", os.environ.get("MARKETPLACE_FEE_PERCENT", "1.0")))

    @property
    def DEX_FEE_PERCENT(self) -> float:
        return float(self._raw_config.get("DEX_FEE_PERCENT", os.environ.get("DEX_FEE_PERCENT", "0.05")))


config = Config.get()
