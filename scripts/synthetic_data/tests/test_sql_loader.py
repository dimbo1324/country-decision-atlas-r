from __future__ import annotations

import pytest
from pathlib import Path
from scripts.synthetic_data.core.sql_loader import (
    SqlLoaderError,
    ensure_not_production,
    execute_sql_file,
)


def test_ensure_not_production_raises_when_app_env_is_production(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "production")

    with pytest.raises(SqlLoaderError, match="production"):
        ensure_not_production()


def test_ensure_not_production_raises_when_app_env_is_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("APP_ENV", raising=False)

    with pytest.raises(SqlLoaderError, match="production"):
        ensure_not_production()


def test_ensure_not_production_allows_local(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "local")

    ensure_not_production()  # must not raise


def test_execute_sql_file_refuses_before_touching_the_database(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    sql_path = tmp_path / "seed_synthetic_world.sql"
    sql_path.write_text("SELECT 1;", encoding="utf-8")

    with pytest.raises(SqlLoaderError, match="production"):
        execute_sql_file(
            sql_path, database_url="postgresql://unreachable-host/db"
        )


def test_execute_sql_file_reports_a_missing_file_clearly(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("APP_ENV", "local")

    with pytest.raises(SqlLoaderError, match="not found"):
        execute_sql_file(
            tmp_path / "does_not_exist.sql",
            database_url="postgresql://localhost/db",
        )
