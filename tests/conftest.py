"""Shared test fixtures for MangroveMarkets."""
import pytest

from src.shared.config import _Config


@pytest.fixture(autouse=True)
def reset_config():
    """Reset config singleton between tests."""
    _Config.reset()
    yield
    _Config.reset()
