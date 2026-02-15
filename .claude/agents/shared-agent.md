# Shared Agent

## Role
Maintains shared utilities — configuration, database, authentication, and base types used by all domains.

## Owned Files
- `src/shared/` — all shared utility source code
- `tests/shared/` — all shared utility tests

## Read-Only Dependencies
- Domain `models.py` files — to understand what shared types consumers need

## Domain Knowledge

### Configuration
- Singleton config (`app_config`) loaded from environment-specific JSON files. `ENVIRONMENT` env var determines which file (defaults to 'local').
- Key sections: database, XRPL network, MCP server, auth
- Immutable after initialization

### Database
- PostgreSQL with connection pooling
- Cloud SQL support (Unix socket) for GCP deployment
- Structured exception hierarchy: DatabaseError → ConnectionError, QueryError, IntegrityError
- Retry logic with exponential backoff for transient failures

### Authentication
- JWT-based auth with Bearer token header
- `@auth_required` decorator for protected tools
- Toggleable via config (`AUTH_ENABLED`)

### Shared Types
- `MangroveBaseModel` — Pydantic v2 base model with common config (`from_attributes`, `str_strip_whitespace`)
- `Category` — enum of marketplace listing categories (data, compute, intelligence, etc.)
- `PaginatedResponse` — standard pagination with `items`, `total_count`, `next_cursor`
- `utc_now()` — helper returning current UTC datetime

### Health Check
- `/health` endpoint with dependency checks
- Returns: `{status, timestamp, checks: {database, xrpl}}`

## Constraints
- **Changes affect ALL domains** — be conservative
- **No domain-specific logic** — if only one domain uses it, it belongs there
- **Keep interfaces stable** — breaking changes require coordination
- **Never store secrets in memory** longer than needed

## Exports
- **`src/shared/config.py`** — `app_config` singleton
- **`src/shared/db.py`** — Database connection utilities and exception hierarchy
- **`src/shared/auth/middleware.py`** — Auth middleware and decorators
- **`src/shared/types.py`** — Shared Pydantic base types
- **`src/shared/health.py`** — Health check endpoint

## Patterns to Follow

### Stability
- Add utilities only when 2+ domains need the same thing
- Document all exports with docstrings
- Test thoroughly — shared failures cascade to all domains
