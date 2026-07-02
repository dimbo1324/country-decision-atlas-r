from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = ROOT_DIR / "scripts"


@dataclass(frozen=True)
class ScriptInfo:
    key: str
    filename: str
    title: str
    description: str


AVAILABLE_SCRIPTS: list[ScriptInfo] = [
    ScriptInfo(
        key="1",
        filename="script1.py",
        title="script1",
        description="Prints 'Hello World' to the console.",
    ),
    ScriptInfo(
        key="2",
        filename="script2.py",
        title="script2",
        description="Generates two random numbers and prints their sum.",
    ),
    ScriptInfo(
        key="3",
        filename="script3.py",
        title="script3",
        description="Shows a small system/runtime demo message.",
    ),
]

DEFAULT_SCRIPT_KEY = "1"


def print_menu() -> None:
    print("\nPython Script Orchestrator")
    print("=" * 30)
    print("Choose which script to run. Press Enter to run the default script.\n")

    for script in AVAILABLE_SCRIPTS:
        default_marker = " [default]" if script.key == DEFAULT_SCRIPT_KEY else ""
        print(f"{script.key}. {script.title}{default_marker}")
        print(f"   {script.description}")

    print("\nYou can type either the number or the script name, for example: 1 or script1.")


def normalize_choice(raw_choice: str) -> str:
    choice = raw_choice.strip().lower()
    if not choice:
        return DEFAULT_SCRIPT_KEY

    for script in AVAILABLE_SCRIPTS:
        if choice in {script.key, script.title.lower(), script.filename.lower()}:
            return script.key

    return choice


def find_script(choice: str) -> ScriptInfo | None:
    normalized = normalize_choice(choice)
    for script in AVAILABLE_SCRIPTS:
        if script.key == normalized:
            return script
    return None


def run_script(script: ScriptInfo) -> int:
    script_path = SCRIPTS_DIR / script.filename

    if not script_path.exists():
        print(f"ERROR: script file not found: {script_path}", file=sys.stderr)
        return 1

    print(f"\nRunning {script.title}...", flush=True)
    print("-" * 30, flush=True)

    completed_process = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=ROOT_DIR,
        check=False,
    )

    print("-" * 30)
    print(f"Finished {script.title} with exit code {completed_process.returncode}.")
    return completed_process.returncode


def main() -> int:
    print_menu()
    choice = input("Your choice [default: 1/script1]: ")
    script = find_script(choice)

    if script is None:
        print(f"\nUnknown choice: {choice!r}", file=sys.stderr)
        print("Please run the orchestrator again and choose one of the listed scripts.")
        return 2

    return run_script(script)


if __name__ == "__main__":
    raise SystemExit(main())
