from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from uuid import uuid4


ROOT_DIR = Path(__file__).resolve().parents[1]
SCRATCH_IMAGE = "postgres:16-alpine"
SCRATCH_PASSWORD = "scratch-restore-check"
READY_TIMEOUT_SECONDS = 30
READY_POLL_SECONDS = 1


def scratch_container_name() -> str:
    return f"cda-restore-check-{uuid4().hex[:8]}"


def run_container_command(
    docker_exe: str, name: str, user: str, database: str
) -> list[str]:
    # POSTGRES_USER must match the role that owns the real database's
    # objects: a plain pg_dump (no --no-owner) emits `ALTER ... OWNER TO`/
    # `GRANT ... TO` statements for that role, which fail against a scratch
    # container that only has the default "postgres" superuser. Matching it
    # here also makes the restore drill a closer analog of a real recovery,
    # instead of silently stripping ownership info from the dump.
    return [
        docker_exe,
        "run",
        "--rm",
        "-d",
        "--name",
        name,
        "-e",
        f"POSTGRES_USER={user}",
        "-e",
        f"POSTGRES_PASSWORD={SCRATCH_PASSWORD}",
        "-e",
        f"POSTGRES_DB={database}",
        SCRATCH_IMAGE,
    ]


def readiness_command(docker_exe: str, name: str, user: str) -> list[str]:
    return [docker_exe, "exec", name, "pg_isready", "-U", user]


def restore_command(
    docker_exe: str, name: str, user: str, database: str
) -> list[str]:
    return [
        docker_exe,
        "exec",
        "-i",
        name,
        "psql",
        "-U",
        user,
        "-d",
        database,
        "-v",
        "ON_ERROR_STOP=1",
    ]


def integrity_check_command(
    docker_exe: str, name: str, user: str, database: str
) -> list[str]:
    return [
        docker_exe,
        "exec",
        name,
        "psql",
        "-U",
        user,
        "-d",
        database,
        "-tAc",
        "SELECT COUNT(*) FROM schema_migrations",
    ]


def stop_command(docker_exe: str, name: str) -> list[str]:
    return [docker_exe, "stop", name]


def wait_for_readiness(
    docker_exe: str,
    name: str,
    user: str,
    *,
    timeout_seconds: float = READY_TIMEOUT_SECONDS,
    poll_seconds: float = READY_POLL_SECONDS,
    sleep: object = time.sleep,
) -> None:
    deadline = time.monotonic() + timeout_seconds
    command = readiness_command(docker_exe, name, user)
    while True:
        result = subprocess.run(command, capture_output=True, check=False)
        if result.returncode == 0:
            return
        if time.monotonic() >= deadline:
            raise RuntimeError(
                f"Scratch container {name} did not become ready within "
                f"{timeout_seconds}s"
            )
        sleep(poll_seconds)  # type: ignore[operator]


def run_restore_check(
    *,
    backup_file: Path,
    user: str,
    database: str,
    dry_run: bool,
    docker_exe: str | None,
) -> dict[str, object]:
    if not backup_file.exists():
        raise RuntimeError(f"Backup file not found: {backup_file}")

    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "backup_file": str(backup_file),
            "database": database,
        }

    if docker_exe is None:
        raise RuntimeError("docker executable not found on PATH")

    name = scratch_container_name()
    start = subprocess.run(
        run_container_command(docker_exe, name, user, database),
        cwd=ROOT_DIR,
        capture_output=True,
        check=False,
    )
    if start.returncode != 0:
        raise RuntimeError(
            "Failed to start scratch container: "
            f"{start.stderr.decode('utf-8', errors='replace').strip()}"
        )

    try:
        wait_for_readiness(docker_exe, name, user)

        with backup_file.open("rb") as dump_file:
            restored = subprocess.run(
                restore_command(docker_exe, name, user, database),
                stdin=dump_file,
                capture_output=True,
                check=False,
            )
        if restored.returncode != 0:
            raise RuntimeError(
                "Restore failed: "
                f"{restored.stderr.decode('utf-8', errors='replace').strip()}"
            )

        checked = subprocess.run(
            integrity_check_command(docker_exe, name, user, database),
            capture_output=True,
            check=False,
        )
        if checked.returncode != 0:
            raise RuntimeError(
                "Integrity check query failed: "
                f"{checked.stderr.decode('utf-8', errors='replace').strip()}"
            )
        schema_migrations_count = int(
            checked.stdout.decode("utf-8").strip() or "0"
        )

        return {
            "ok": schema_migrations_count > 0,
            "dry_run": False,
            "backup_file": str(backup_file),
            "database": database,
            "schema_migrations_count": schema_migrations_count,
            "container": name,
        }
    finally:
        subprocess.run(
            stop_command(docker_exe, name), capture_output=True, check=False
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Restore a pg_dump backup into a disposable scratch "
        "Postgres container (never the real database) and verify "
        "schema_migrations is populated, then discard the container. "
        "Intended as a periodic backup-integrity smoke check."
    )
    parser.add_argument("--backup-file", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true", default=False)
    args = parser.parse_args()

    user = os.environ.get("POSTGRES_USER", "country_atlas")
    database = os.environ.get("POSTGRES_DB", "country_atlas")
    docker_exe = shutil.which("docker")

    try:
        result = run_restore_check(
            backup_file=args.backup_file,
            user=user,
            database=database,
            dry_run=args.dry_run,
            docker_exe=docker_exe,
        )
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1

    print(json.dumps(result, default=str))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
