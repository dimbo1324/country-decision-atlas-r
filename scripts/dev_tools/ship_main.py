from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]


def resolve_command(command: list[str]) -> list[str]:
    return [shutil.which(command[0]) or command[0], *command[1:]]


def run(command: list[str], *, check: bool = True) -> int:
    print(f"$ {subprocess.list2cmdline(command)}")
    completed_process = subprocess.run(
        resolve_command(command),
        cwd=ROOT_DIR,
        check=False,
    )
    if check and completed_process.returncode != 0:
        raise SystemExit(completed_process.returncode)
    return completed_process.returncode


def output(command: list[str]) -> str:
    completed_process = subprocess.run(
        resolve_command(command),
        cwd=ROOT_DIR,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return completed_process.stdout.strip()


def has_changes() -> bool:
    return bool(output(["git", "status", "--porcelain"]))


def current_branch() -> str:
    return output(["git", "rev-parse", "--abbrev-ref", "HEAD"])


def ensure_main_branch() -> None:
    branch = current_branch()
    if branch != "main":
        raise SystemExit(
            f"Refusing to ship from branch {branch!r}. Switch to main first."
        )


def ensure_dependencies() -> None:
    run(["corepack", "pnpm@9.12.0", "install", "--frozen-lockfile"])


def format_code() -> None:
    run([sys.executable, "scripts/dev_tools/format_code.py"])


def commit_changes(message: str) -> None:
    run(["git", "add", "-A"])
    if not has_changes():
        print("No changes to commit.")
        return

    run(["git", "commit", "-m", message])


def quick_gate() -> None:
    run([sys.executable, "dev_tools_scripts_runner.py", "--profile", "quick"])


def push_main(*, verified: bool) -> None:
    run(["git", "pull", "--ff-only", "origin", "main"])
    push_command = ["git", "push", "origin", "main"]
    if verified:
        push_command.insert(2, "--no-verify")
    run(push_command)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Format, commit, verify, and push main safely."
    )
    parser.add_argument(
        "--message",
        "-m",
        required=True,
        help="Commit message for the current logical change.",
    )
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="Skip pnpm install when node_modules are already known-good.",
    )
    parser.add_argument(
        "--skip-format",
        action="store_true",
        help="Skip the formatter step.",
    )
    parser.add_argument(
        "--skip-push",
        action="store_true",
        help="Commit and verify, but do not push.",
    )
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="Skip the quick quality gate. Use only for emergency local commits.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    ensure_main_branch()

    if not args.skip_install:
        ensure_dependencies()
    if not args.skip_format:
        format_code()

    commit_changes(args.message)

    verified = False
    if not args.no_verify:
        quick_gate()
        verified = True
    if not args.skip_push:
        push_main(verified=verified)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
