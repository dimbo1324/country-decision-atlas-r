from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
PYTHON_PATHS = ["apps", "packages", "scripts", "tests", "utils"]
TARGET_ORDER = ("python", "frontend", "go")


def run(command: list[str]) -> int:
    print(f"$ {subprocess.list2cmdline(command)}")
    resolved_command = [shutil.which(command[0]) or command[0], *command[1:]]
    completed_process = subprocess.run(
        resolved_command,
        cwd=ROOT_DIR,
        check=False,
    )
    return completed_process.returncode


def format_python() -> int:
    check_code = run(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            "--fix",
            *PYTHON_PATHS,
        ]
    )
    if check_code != 0:
        return check_code

    return run([sys.executable, "-m", "ruff", "format", *PYTHON_PATHS])


def format_frontend() -> int:
    return run(["corepack", "pnpm@9.12.0", "format:prettier"])


def format_go() -> int:
    files = sorted(
        str(path) for path in (ROOT_DIR / "apps" / "notifier").rglob("*.go")
    )
    if not files:
        return 0

    return run(["gofmt", "-w", *files])


def parse_targets(raw_targets: list[str]) -> list[str]:
    if not raw_targets or "all" in raw_targets:
        return list(TARGET_ORDER)

    return [target for target in TARGET_ORDER if target in set(raw_targets)]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Format all code surfaces.")
    parser.add_argument(
        "targets",
        nargs="*",
        choices=(*TARGET_ORDER, "all"),
        help="Optional formatter targets. Defaults to all.",
    )
    args = parser.parse_args(argv)

    formatters = {
        "python": format_python,
        "frontend": format_frontend,
        "go": format_go,
    }

    for target in parse_targets(args.targets):
        return_code = formatters[target]()
        if return_code != 0:
            return return_code

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
