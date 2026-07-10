from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT_DIR / "backups" / "postgres"
DEFAULT_SERVICE = "postgres"


def backup_filename(now: datetime, database: str) -> str:
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    return f"{database}-{stamp}.sql"


def dump_command(
    docker_exe: str, service: str, user: str, database: str
) -> list[str]:
    return [
        docker_exe,
        "compose",
        "exec",
        "-T",
        service,
        "pg_dump",
        "-U",
        user,
        database,
    ]


def run_backup(
    *,
    output_dir: Path,
    service: str,
    user: str,
    database: str,
    dry_run: bool,
    docker_exe: str | None,
) -> dict[str, object]:
    now = datetime.now(UTC)
    output_path = output_dir / backup_filename(now, database)
    command = dump_command(docker_exe or "docker", service, user, database)

    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "path": str(output_path),
            "command": command,
        }

    if docker_exe is None:
        raise RuntimeError("docker executable not found on PATH")

    output_dir.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as dump_file:
        result = subprocess.run(
            command,
            cwd=ROOT_DIR,
            stdout=dump_file,
            stderr=subprocess.PIPE,
            check=False,
        )

    if result.returncode != 0:
        output_path.unlink(missing_ok=True)
        raise RuntimeError(
            f"pg_dump failed (exit {result.returncode}): "
            f"{result.stderr.decode('utf-8', errors='replace').strip()}"
        )

    return {
        "ok": True,
        "dry_run": False,
        "path": str(output_path),
        "size_bytes": output_path.stat().st_size,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Back up the postgres service's database with pg_dump, "
        "run through `docker compose exec` against the already-running "
        "stack. Intended to run on a recurring schedule (cron/systemd "
        "timer/CronJob) once a deployment target exists."
    )
    parser.add_argument(
        "--output-dir", default=str(DEFAULT_OUTPUT_DIR), type=Path
    )
    parser.add_argument("--service", default=DEFAULT_SERVICE)
    parser.add_argument("--dry-run", action="store_true", default=False)
    args = parser.parse_args()

    user = os.environ.get("POSTGRES_USER", "country_atlas")
    database = os.environ.get("POSTGRES_DB", "country_atlas")
    docker_exe = shutil.which("docker")

    try:
        result = run_backup(
            output_dir=args.output_dir,
            service=args.service,
            user=user,
            database=database,
            dry_run=args.dry_run,
            docker_exe=docker_exe,
        )
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1

    print(json.dumps(result, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
