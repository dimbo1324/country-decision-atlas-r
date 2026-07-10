"""Postgres backup script: filename/command construction, dry-run, and pg_dump failure handling (P2-10, Аудит-эпизод 6)."""

import pytest
import scripts.backup_postgres as backup_script
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock


def test_backup_filename_is_timestamped_and_sortable() -> None:
    now = datetime(2026, 7, 10, 9, 2, 4, tzinfo=UTC)
    assert (
        backup_script.backup_filename(now, "country_atlas")
        == "country_atlas-20260710T090204Z.sql"
    )


def test_dump_command_uses_docker_compose_exec() -> None:
    command = backup_script.dump_command(
        "docker", "postgres", "country_atlas", "country_atlas"
    )
    assert command == [
        "docker",
        "compose",
        "exec",
        "-T",
        "postgres",
        "pg_dump",
        "-U",
        "country_atlas",
        "country_atlas",
    ]


def test_dry_run_reports_plan_without_touching_docker_or_filesystem(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "backups"
    result = backup_script.run_backup(
        output_dir=output_dir,
        service="postgres",
        user="country_atlas",
        database="country_atlas",
        dry_run=True,
        docker_exe=None,
    )
    assert result["ok"] is True
    assert result["dry_run"] is True
    assert not output_dir.exists()


def test_real_run_writes_pg_dump_stdout_to_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_dir = tmp_path / "backups"

    def fake_run(_command: Any, *, stdout: Any, **_kwargs: Any) -> MagicMock:
        stdout.write(b"-- dump contents\n")
        result = MagicMock()
        result.returncode = 0
        return result

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = backup_script.run_backup(
        output_dir=output_dir,
        service="postgres",
        user="country_atlas",
        database="country_atlas",
        dry_run=False,
        docker_exe="docker",
    )

    assert result["ok"] is True
    assert result["dry_run"] is False
    written = Path(str(result["path"]))
    assert written.read_bytes() == b"-- dump contents\n"
    assert result["size_bytes"] == written.stat().st_size


def test_real_run_raises_and_removes_partial_file_on_pg_dump_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_dir = tmp_path / "backups"

    def fake_run(_command: Any, *, stdout: Any, **_kwargs: Any) -> MagicMock:
        stdout.write(b"partial")
        result = MagicMock()
        result.returncode = 1
        result.stderr = b"connection refused"
        return result

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(RuntimeError, match="pg_dump failed"):
        backup_script.run_backup(
            output_dir=output_dir,
            service="postgres",
            user="country_atlas",
            database="country_atlas",
            dry_run=False,
            docker_exe="docker",
        )

    assert list(output_dir.glob("*.sql")) == []


def test_real_run_without_docker_raises() -> None:
    with pytest.raises(RuntimeError, match="docker executable not found"):
        backup_script.run_backup(
            output_dir=Path("unused"),
            service="postgres",
            user="country_atlas",
            database="country_atlas",
            dry_run=False,
            docker_exe=None,
        )
