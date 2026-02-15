import psycopg2
from typing import Optional


class DatabaseError(Exception):
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.original_error = original_error

    def __str__(self):
        if self.original_error:
            return f"{self.message} (Original error: {str(self.original_error)})"
        return self.message


class ConnectionError(DatabaseError):
    pass


class IntegrityError(DatabaseError):
    pass


class QueryError(DatabaseError):
    pass


class TransactionError(DatabaseError):
    pass


class NotFoundError(DatabaseError):
    pass


class DuplicateError(IntegrityError):
    pass


def map_psycopg2_exception(exc: Exception, context: str = "") -> DatabaseError:
    context_prefix = f"{context}: " if context else ""

    if isinstance(exc, psycopg2.OperationalError):
        return ConnectionError(
            f"{context_prefix}Database connection failed",
            original_error=exc,
        )

    if isinstance(exc, psycopg2.IntegrityError):
        error_msg = str(exc).lower()

        if "foreign key" in error_msg:
            return IntegrityError(f"{context_prefix}Foreign key constraint violated", exc)
        if "unique" in error_msg or "duplicate" in error_msg:
            return DuplicateError(f"{context_prefix}Duplicate record detected", exc)
        if "check" in error_msg:
            return IntegrityError(f"{context_prefix}Check constraint violated", exc)
        if "not null" in error_msg or "null value" in error_msg:
            return IntegrityError(f"{context_prefix}Required field cannot be null", exc)

        return IntegrityError(f"{context_prefix}Database integrity constraint violated", exc)

    if isinstance(exc, psycopg2.ProgrammingError):
        return QueryError(f"{context_prefix}Invalid query or database object", exc)

    if isinstance(exc, psycopg2.DataError):
        return QueryError(f"{context_prefix}Invalid data for database operation", exc)

    if isinstance(exc, psycopg2.InternalError):
        return TransactionError(f"{context_prefix}Database transaction error", exc)

    if isinstance(exc, psycopg2.Error):
        return DatabaseError(f"{context_prefix}Database error: {str(exc)}", exc)

    return DatabaseError(f"{context_prefix}Unexpected error: {str(exc)}", exc)
