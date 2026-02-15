"""Structured error and success response utilities for MCP tools."""
import json
from typing import Any


def tool_error(code: str, message: str, suggestion: str = "") -> str:
    """Return a structured error response as JSON string.

    All MCP tools use this for error responses to ensure consistency.
    """
    return json.dumps({
        "error": True,
        "code": code,
        "message": message,
        "suggestion": suggestion,
    })


def tool_success(data: Any) -> str:
    """Return a structured success response as JSON string."""
    if isinstance(data, dict):
        return json.dumps(data)
    if hasattr(data, "model_dump"):
        return json.dumps(data.model_dump())
    return json.dumps(data)
