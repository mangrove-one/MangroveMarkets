"""Shared test fixtures for MangroveMarkets."""
import pytest

from src.shared.config import Config


@pytest.fixture(autouse=True)
def reset_config():
    """Reset config singleton between tests."""
    Config.reset()
    yield
    Config.reset()
