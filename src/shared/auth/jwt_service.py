"""JWT token creation and verification utilities."""
import datetime
from typing import Any

import jwt

from src.shared.config import app_config


def create_token(payload: dict[str, Any], expires_in_seconds: int = 3600) -> str:
    """Create a JWT token with expiry."""
    exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=expires_in_seconds)
    token_payload = {**payload, "exp": exp}
    return jwt.encode(token_payload, app_config.JWT_SECRET, algorithm="HS256")


def verify_token(token: str) -> dict[str, Any]:
    """Verify and decode a JWT token."""
    return jwt.decode(token, app_config.JWT_SECRET, algorithms=["HS256"])
