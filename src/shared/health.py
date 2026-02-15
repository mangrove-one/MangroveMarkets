"""Health check endpoint for MangroveMarkets."""
from datetime import datetime, timezone


def health_payload() -> dict:
    """Return health check payload."""
    return {
        "status": "healthy",
        "service": "MangroveMarkets",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
