from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[3]
_API_DIR = ROOT_DIR / "apps" / "api"


class SqlLoaderError(RuntimeError):
    pass


def _current_app_env() -> str:
    """Read the same `APP_ENV` the API app reads, without importing its
    full settings module (which requires secrets/config this standalone
    script has no business needing just to check one flag)."""
    return os.environ.get("APP_ENV", "production")


def ensure_not_production() -> None:
    """Refuse before ever opening a database connection if the environment
    looks like production (spec section 11.2: "отказываться запускаться на
    production-конфигурации"). `APP_ENV` defaults to `"production"` — the
    same fail-closed default `apps/api/app/core/config.py` uses — so an
    unset environment is treated as production, not as local."""
    app_env = _current_app_env()
    if app_env == "production":
        raise SqlLoaderError(
            "Refusing to load synthetic SQL fixtures: APP_ENV=production "
            "(or unset). Set APP_ENV=local (as docker-compose.yml and "
            ".env.example do for local development) to proceed."
        )


def execute_sql_file(sql_path: Path, *, database_url: str) -> None:
    ensure_not_production()
    if not sql_path.exists():
        raise SqlLoaderError(f"SQL file not found: {sql_path}")

    if str(_API_DIR) not in sys.path:
        sys.path.insert(0, str(_API_DIR))
    import psycopg

    sql_text = sql_path.read_text(encoding="utf-8")
    # autocommit=True: the SQL file already wraps itself in its own
    # BEGIN/COMMIT (sql_fixture.py), so psycopg must not also open an
    # implicit outer transaction around it.
    with psycopg.connect(database_url, autocommit=True) as connection:
        connection.execute(sql_text)
