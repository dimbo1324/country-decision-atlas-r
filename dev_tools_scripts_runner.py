from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys


ROOT_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = ROOT_DIR / "scripts" / "dev_tools"


@dataclass(frozen=True)
class ScriptInfo:
    key: str
    filename: str
    title: str
    description: str


# Add new scripts here as they're placed in scripts/dev_tools/ — no other
# changes are needed for the orchestrator to pick them up.
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
    ),
]

DEFAULT_SCRIPT_KEY = "1"


def find_script(choice: str) -> ScriptInfo | None:
    normalized = choice.strip().lower()
    for script in AVAILABLE_SCRIPTS:
        if normalized in {script.key, script.title.lower(), script.filename.lower()}:
            return script
    return None


def default_script() -> ScriptInfo:
    script = find_script(DEFAULT_SCRIPT_KEY)
    assert script is not None, "DEFAULT_SCRIPT_KEY must match a registered script"
    return script


def print_menu() -> None:
    print("\nCountry Decision Atlas — script orchestrator")
    print("=" * 46)
    print("Choose which script to run. Press Enter to run the default script.\n")

    for script in AVAILABLE_SCRIPTS:
        default_marker = " [default]" if script.key == DEFAULT_SCRIPT_KEY else ""
        print(f"{script.key}. {script.title}{default_marker}")
        print(f"   {script.description}")

    print(
        "\nYou can type either the number or the script name, "
        f"for example: {DEFAULT_SCRIPT_KEY} or {default_script().title}."
    )


def run_script(script: ScriptInfo, extra_args: list[str]) -> int:
    script_path = SCRIPTS_DIR / script.filename

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
        print("Please run the orchestrator again and choose one of the listed scripts.")
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
