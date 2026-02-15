"""Database exception hierarchy for MangroveMarkets."""
from typing import Optional

import psycopg2


class DatabaseError(Exception):
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.original_error = original_error


class DatabaseConnectionError(DatabaseError):
    pass


class IntegrityError(DatabaseError):
    pass


class QueryError(DatabaseError):
    pass


class NotFoundError(DatabaseError):
    pass


class DuplicateError(IntegrityError):
    pass


def map_psycopg2_exception(exc: Exception, context: str = "") -> DatabaseError:
    """Map psycopg2 exceptions to domain-specific database errors."""
    prefix = f"{context}: " if context else ""

    if isinstance(exc, psycopg2.OperationalError):
        return DatabaseConnectionError(f"{prefix}Database connection failed", exc)

    if isinstance(exc, psycopg2.IntegrityError):
        msg = str(exc).lower()
        if "unique" in msg or "duplicate" in msg:
            return DuplicateError(f"{prefix}Duplicate record", exc)
        return IntegrityError(f"{prefix}Integrity constraint violated", exc)

    if isinstance(exc, psycopg2.ProgrammingError):
        return QueryError(f"{prefix}Invalid query", exc)

    if isinstance(exc, psycopg2.Error):
        return DatabaseError(f"{prefix}Database error: {exc}", exc)

    return DatabaseError(f"{prefix}Unexpected error: {exc}", exc)
