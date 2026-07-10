"""Postgres restore-check script: command construction, dry-run, readiness wait, and scratch-container cleanup (P2-10, Аудит-эпизод 6)."""

import pytest
import scripts.restore_postgres_check as restore_script
import subprocess
import time
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock


def test_scratch_container_name_has_stable_prefix() -> None:
    name = restore_script.scratch_container_name()
    assert name.startswith("cda-restore-check-")


def test_scratch_container_names_are_unique() -> None:
    names = {restore_script.scratch_container_name() for _ in range(20)}
    assert len(names) == 20


def test_run_container_command_never_touches_the_real_database() -> None:
    command = restore_script.run_container_command(
        "docker", "cda-restore-check-abc123", "country_atlas", "country_atlas"
    )
    assert command == [
        "docker",
        "run",
        "--rm",
        "-d",
        "--name",
        "cda-restore-check-abc123",
        "-e",
        "POSTGRES_USER=country_atlas",
        "-e",
        "POSTGRES_PASSWORD=scratch-restore-check",
        "-e",
        "POSTGRES_DB=country_atlas",
        "postgres:16-alpine",
    ]


def test_restore_command_stops_on_first_error() -> None:
    command = restore_script.restore_command(
        "docker", "cda-restore-check-abc123", "country_atlas", "country_atlas"
    )
    assert "-v" in command
    assert "ON_ERROR_STOP=1" in command


def test_integrity_check_command_queries_schema_migrations() -> None:
    command = restore_script.integrity_check_command(
        "docker", "cda-restore-check-abc123", "country_atlas", "country_atlas"
    )
    assert "SELECT COUNT(*) FROM schema_migrations" in command


def test_dry_run_reports_plan_without_touching_docker(
    tmp_path: Path,
) -> None:
    backup_file = tmp_path / "backup.sql"
    backup_file.write_text("-- dump")

    result = restore_script.run_restore_check(
        backup_file=backup_file,
        user="country_atlas",
        database="country_atlas",
        dry_run=True,
        docker_exe=None,
    )

    assert result == {
        "ok": True,
        "dry_run": True,
        "backup_file": str(backup_file),
        "database": "country_atlas",
    }


def test_dry_run_still_validates_backup_file_exists(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="Backup file not found"):
        restore_script.run_restore_check(
            backup_file=tmp_path / "missing.sql",
            user="country_atlas",
            database="country_atlas",
            dry_run=True,
            docker_exe=None,
        )


def test_real_run_without_docker_raises(tmp_path: Path) -> None:
    backup_file = tmp_path / "backup.sql"
    backup_file.write_text("-- dump")

    with pytest.raises(RuntimeError, match="docker executable not found"):
        restore_script.run_restore_check(
            backup_file=backup_file,
            user="country_atlas",
            database="country_atlas",
            dry_run=False,
            docker_exe=None,
        )


def test_wait_for_readiness_polls_until_pg_isready_succeeds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    attempts = [
        MagicMock(returncode=1),
        MagicMock(returncode=1),
        MagicMock(returncode=0),
    ]
    calls: list[Any] = []

    def fake_run(command: Any, **_kwargs: Any) -> MagicMock:
        calls.append(command)
        return attempts.pop(0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    sleeps: list[float] = []

    restore_script.wait_for_readiness(
        "docker",
        "cda-restore-check-abc123",
        "country_atlas",
        sleep=sleeps.append,
    )

    assert len(calls) == 3
    assert sleeps == [1, 1]


def test_wait_for_readiness_times_out(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *_a, **_kw: MagicMock(returncode=1),
    )
    clock = iter([0.0, 0.0, 40.0])
    monkeypatch.setattr(time, "monotonic", lambda: next(clock))

    with pytest.raises(RuntimeError, match="did not become ready"):
        restore_script.wait_for_readiness(
            "docker",
            "cda-restore-check-abc123",
            "country_atlas",
            sleep=lambda _s: None,
        )


def test_real_run_happy_path_reports_schema_migrations_count_and_stops_container(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    backup_file = tmp_path / "backup.sql"
    backup_file.write_text("-- dump")
    calls: list[list[str]] = []

    def fake_run(command: Any, **_kwargs: Any) -> MagicMock:
        calls.append(command)
        if "pg_isready" in command:
            return MagicMock(returncode=0)
        if command[:2] == ["docker", "run"]:
            return MagicMock(returncode=0, stderr=b"")
        if "psql" in command and "ON_ERROR_STOP=1" in command:
            return MagicMock(returncode=0, stderr=b"")
        if "SELECT COUNT(*) FROM schema_migrations" in command:
            return MagicMock(returncode=0, stdout=b"42\n")
        if command[:2] == ["docker", "stop"]:
            return MagicMock(returncode=0)
        raise AssertionError(f"unexpected command: {command}")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = restore_script.run_restore_check(
        backup_file=backup_file,
        user="country_atlas",
        database="country_atlas",
        dry_run=False,
        docker_exe="docker",
    )

    assert result["ok"] is True
    assert result["schema_migrations_count"] == 42
    stop_calls = [c for c in calls if c[:2] == ["docker", "stop"]]
    assert len(stop_calls) == 1


def test_real_run_stops_container_even_when_restore_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    backup_file = tmp_path / "backup.sql"
    backup_file.write_text("-- dump")
    calls: list[list[str]] = []

    def fake_run(command: Any, **_kwargs: Any) -> MagicMock:
        calls.append(command)
        if "pg_isready" in command:
            return MagicMock(returncode=0)
        if command[:2] == ["docker", "run"]:
            return MagicMock(returncode=0, stderr=b"")
        if "psql" in command and "ON_ERROR_STOP=1" in command:
            return MagicMock(returncode=1, stderr=b"syntax error")
        if command[:2] == ["docker", "stop"]:
            return MagicMock(returncode=0)
        raise AssertionError(f"unexpected command: {command}")

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(RuntimeError, match="Restore failed"):
        restore_script.run_restore_check(
            backup_file=backup_file,
            user="country_atlas",
            database="country_atlas",
            dry_run=False,
            docker_exe="docker",
        )

    stop_calls = [c for c in calls if c[:2] == ["docker", "stop"]]
    assert len(stop_calls) == 1


def test_zero_schema_migrations_is_reported_as_not_ok(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    backup_file = tmp_path / "backup.sql"
    backup_file.write_text("-- dump")

    def fake_run(command: Any, **_kwargs: Any) -> MagicMock:
        if "pg_isready" in command:
            return MagicMock(returncode=0)
        if command[:2] == ["docker", "run"]:
            return MagicMock(returncode=0, stderr=b"")
        if "psql" in command and "ON_ERROR_STOP=1" in command:
            return MagicMock(returncode=0, stderr=b"")
        if "SELECT COUNT(*) FROM schema_migrations" in command:
            return MagicMock(returncode=0, stdout=b"0\n")
        if command[:2] == ["docker", "stop"]:
            return MagicMock(returncode=0)
        raise AssertionError(f"unexpected command: {command}")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = restore_script.run_restore_check(
        backup_file=backup_file,
        user="country_atlas",
        database="country_atlas",
        dry_run=False,
        docker_exe="docker",
    )

    assert result["ok"] is False
    assert result["schema_migrations_count"] == 0
