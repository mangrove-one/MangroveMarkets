import datetime
from typing import Dict

import jwt

from app_core.config import app_config


def create_token(payload: Dict[str, str], expires_in_seconds: int = 3600) -> str:
    exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in_seconds)
    token_payload = {**payload, "exp": exp}
    return jwt.encode(token_payload, app_config.JWT_SECRET, algorithm="HS256")


def verify_token(token: str) -> Dict[str, str]:
    return jwt.decode(token, app_config.JWT_SECRET, algorithms=["HS256"])
