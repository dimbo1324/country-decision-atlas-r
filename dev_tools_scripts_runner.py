from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = ROOT_DIR / "scripts" / "dev_tools"


@dataclass(frozen=True)
class ScriptInfo:
    key: str
    filename: str
    title: str
    description: str
    aliases: tuple[str, ...] = ()
    directory: Path = SCRIPTS_DIR


# Add new scripts here as they're placed in scripts/dev_tools/ (default
# directory) or elsewhere under scripts/ (set directory= explicitly) — no
# other changes are needed for the orchestrator to pick them up.
AVAILABLE_SCRIPTS: list[ScriptInfo] = [
    ScriptInfo(
        key="1",
        filename="full_check.py",
        title="full-check",
        description=(
            "Runs the local quality gate: toolchain checks, dependency install, "
            "static analysis, tests, and optional Docker/E2E checks. Accepts all "
            "of its own flags unchanged, e.g. --profile, --fix, --doctor."
        ),
        aliases=("check", "quality"),
    ),
    ScriptInfo(
        key="2",
        filename="format_code.py",
        title="format-code",
        description=(
            "Auto-formats Python, frontend/contracts, and Go code. Accepts "
            "optional targets: python, frontend, go, or all."
        ),
        aliases=("format", "fmt"),
    ),
    ScriptInfo(
        key="3",
        filename="ship_main.py",
        title="ship-main",
        description=(
            "Formats, commits, runs the quick gate, fast-forwards from origin/main, "
            "and pushes main. Requires --message."
        ),
        aliases=("ship", "push-main", "publish"),
    ),
    ScriptInfo(
        key="4",
        filename="dispatch_trip_reminders.py",
        title="dispatch-trip-reminders",
        description=(
            "Dispatches due trip reminders into the domain_events outbox "
            "(transactional, idempotent, SKIP LOCKED). Accepts --limit and "
            "--dry-run. Intended to run on a recurring schedule (cron/systemd "
            "timer/CronJob) once a deployment target exists."
        ),
        aliases=("dispatch-reminders", "trip-reminders"),
        directory=ROOT_DIR / "scripts",
    ),
    ScriptInfo(
        key="5",
        filename="sync_agents_md.py",
        title="sync-agents",
        description=(
            "Regenerates AGENTS.md from the shared AI-assistant rule modules "
            "in .ai/ (universal + project). Pass --check to verify sync "
            "without writing."
        ),
        aliases=("sync-agents-md", "agents-sync"),
    ),
]

DEFAULT_SCRIPT_KEY = "1"


def find_script(choice: str) -> ScriptInfo | None:
    normalized = choice.strip().lower()
    for script in AVAILABLE_SCRIPTS:
        choices = {
            script.key,
            script.title.lower(),
            script.filename.lower(),
            *script.aliases,
        }
        if normalized in choices:
            return script
    return None


def default_script() -> ScriptInfo:
    script = find_script(DEFAULT_SCRIPT_KEY)
    assert script is not None, (
        "DEFAULT_SCRIPT_KEY must match a registered script"
    )
    return script


def print_menu() -> None:
    print("\nCountry Decision Atlas — script orchestrator")
    print("=" * 46)
    print("Choose a workflow. Press Enter to run the default full check.\n")

    for script in AVAILABLE_SCRIPTS:
        default_marker = (
            " [default]" if script.key == DEFAULT_SCRIPT_KEY else ""
        )
        print(f"{script.key}. {script.title}{default_marker}")
        print(f"   {script.description}")
        if script.aliases:
            print(f"   aliases: {', '.join(script.aliases)}")

    print(
        "\nExamples:\n"
        "  python dev_tools_scripts_runner.py --profile quick\n"
        "  python dev_tools_scripts_runner.py format-code\n"
        '  python dev_tools_scripts_runner.py ship-main --message "docs: update notes"'
    )


def run_script(script: ScriptInfo, extra_args: list[str]) -> int:
    script_path = script.directory / script.filename

    if not script_path.exists():
        print(f"ERROR: script file not found: {script_path}", file=sys.stderr)
        return 1

    completed_process = subprocess.run(
        [sys.executable, str(script_path), *extra_args],
        cwd=ROOT_DIR,
        check=False,
    )
    return completed_process.returncode


def run_interactive() -> int:
    print_menu()
    raw_choice = input(
        f"Your choice [default: {DEFAULT_SCRIPT_KEY}/{default_script().title}]: "
    )
    choice = raw_choice.strip()
    script = default_script() if not choice else find_script(choice)

    if script is None:
        print(f"\nUnknown choice: {raw_choice!r}", file=sys.stderr)
        print(
            "Please run the orchestrator again and choose one of the listed scripts."
        )
        return 2

    return run_script(script, [])


def main(argv: list[str]) -> int:
    if not argv:
        return run_interactive()

    script = find_script(argv[0])
    if script is not None:
        return run_script(script, argv[1:])

    # The first argument isn't a registered script key/name — treat the whole
    # argv as flags for the default script, so existing invocations like
    # `python dev_tools_scripts_runner.py --profile full --fix` keep working unchanged.
    return run_script(default_script(), argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
