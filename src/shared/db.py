"""Database connection utilities for MangroveMarkets."""
import os
import time
from typing import Optional

import psycopg2

from src.shared.config import config
from src.shared.db_exceptions import ConnectionError, map_psycopg2_exception


def db_connect(max_retries: int = 3, retry_delay: float = 1.0):
    """Create a database connection with retry logic.

    Supports both Cloud SQL (via Unix socket) and standard TCP connections.
    """
    if os.path.exists("/cloudsql"):
        cloud_sql_name = os.environ.get("CLOUD_SQL_CONNECTION_NAME", "")
        if not cloud_sql_name:
            raise ValueError("CLOUD_SQL_CONNECTION_NAME required in Cloud SQL environment")
        return psycopg2.connect(
            host=f"/cloudsql/{cloud_sql_name}",
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
        )

    conn_args = {
        "host": config.DB_HOST,
        "port": config.DB_PORT,
        "dbname": config.DB_NAME,
        "user": config.DB_USER,
    }
    if config.DB_PASSWORD:
        conn_args["password"] = config.DB_PASSWORD

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
