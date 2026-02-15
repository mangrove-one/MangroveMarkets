"""Authentication middleware for MangroveMarkets."""
from functools import wraps

from flask import g, request

from src.shared.config import app_config


def auth_required(f):
    """Decorator to require authentication on Flask routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not app_config.AUTH_ENABLED:
            return f(*args, **kwargs)

        token = _get_token_from_header()
        if not token:
            return {"error": "Unauthorized", "message": "Missing token"}, 401

        g.user_id = "anonymous"
        return f(*args, **kwargs)

    return decorated


def _get_token_from_header() -> str | None:
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1].strip()
    return None
