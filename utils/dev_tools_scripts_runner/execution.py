"""Subprocess execution for registered scripts."""

from __future__ import annotations

import shlex
import subprocess
import sys
from .models import Lang, ScriptInfo
from pathlib import Path


class ScriptRunner:
    """Launches a registered script as a subprocess. The list-form argv
    passed to subprocess.run (never shell=True, never string
    concatenation) is preserved exactly from the original implementation
    -- this is the one place a config/user-derived string reaches a
    process launch, so it stays deliberately boring."""

    def __init__(self, root_dir: Path) -> None:
        self._root_dir = root_dir

    def run(self, script: ScriptInfo, extra_args: list[str]) -> int:
        if not script.path.exists():
            print(
                f"ERROR: script file not found: {script.path}", file=sys.stderr
            )
            return 1

        completed_process = subprocess.run(
            [sys.executable, str(script.path), *extra_args],
            cwd=self._root_dir,
            check=False,
        )
        return completed_process.returncode

    def prompt_extra_args(self, script: ScriptInfo, lang: Lang) -> list[str]:
        prompt = (
            f"Extra arguments for {script.title} (optional, Enter to skip): "
            if lang == "en"
            else f"Дополнительные аргументы для {script.title} "
            "(необязательно, Enter — пропустить): "
        )
        raw = input(prompt).strip()
        return shlex.split(raw) if raw else []

    def launch(self, script: ScriptInfo, lang: Lang) -> int:
        return self.run(script, self.prompt_extra_args(script, lang))
