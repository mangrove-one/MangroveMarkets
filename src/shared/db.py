"""Database connection utilities for MangroveMarkets."""
import os
import time

import psycopg2

from src.shared.config import app_config
from src.shared.db_exceptions import DatabaseConnectionError, map_psycopg2_exception


def db_connect(max_retries: int = 3, retry_delay: float = 1.0):
    """Create a database connection with retry logic.

    Supports both Cloud SQL (via Unix socket) and standard TCP connections.
    """
    if os.path.exists("/cloudsql"):
        cloud_sql_name = app_config.CLOUD_SQL_CONNECTION_NAME or ""
        if not cloud_sql_name:
            raise ValueError("CLOUD_SQL_CONNECTION_NAME required in Cloud SQL environment")
        return psycopg2.connect(
            host=f"/cloudsql/{cloud_sql_name}",
            database=app_config.DB_NAME,
            user=app_config.DB_USER,
            password=app_config.DB_PASSWORD,
        )

    conn_args = {
        "host": app_config.DB_HOST,
        "port": app_config.DB_PORT,
        "dbname": app_config.DB_NAME,
        "user": app_config.DB_USER,
    }
    if app_config.DB_PASSWORD:
        conn_args["password"] = app_config.DB_PASSWORD
    if app_config.DB_SSLMODE and app_config.DB_SSLMODE != "disable":
        conn_args["sslmode"] = app_config.DB_SSLMODE

    last_exception = None
    for attempt in range(max_retries):
        try:
            return psycopg2.connect(**conn_args)
        except psycopg2.OperationalError as e:
            last_exception = e
            error_msg = str(e).lower()
            if any(kw in error_msg for kw in ["password", "authentication"]):
                raise map_psycopg2_exception(e, "connecting to database")
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (2 ** attempt))
        except Exception as e:
            raise map_psycopg2_exception(e, "connecting to database")

    if last_exception:
        raise map_psycopg2_exception(last_exception, f"connecting after {max_retries} attempts")
