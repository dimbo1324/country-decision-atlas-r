from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
MODULES_DIR = ROOT_DIR / ".ai"
AGENTS_MD = ROOT_DIR / "AGENTS.md"

BANNER = """\
<!--
GENERATED FILE - DO NOT EDIT.
Source of truth: .ai/universal/*.md and .ai/project/*.md.
Edit a module, then run: python dev_tools_scripts_runner.py sync-agents
-->

# Country Decision Atlas - working notes for Codex

This file is the Codex entry point. It is assembled from the shared rule
modules in `.ai/` so Codex and Claude Code always follow identical rules.
Later sections override earlier ones; an explicit owner instruction in the
current conversation overrides everything.
"""


def module_files() -> list[Path]:
    groups = ("universal", "project")
    files: list[Path] = []
    for group in groups:
        group_dir = MODULES_DIR / group
        if not group_dir.is_dir():
            print(
                f"ERROR: missing module directory: {group_dir}", file=sys.stderr
            )
            raise SystemExit(2)
        files.extend(sorted(group_dir.glob("*.md")))
    if not files:
        print("ERROR: no rule modules found under .ai/", file=sys.stderr)
        raise SystemExit(2)
    return files


def render() -> str:
    parts = [BANNER]
    for path in module_files():
        body = path.read_text(encoding="utf-8").strip()
        rel = path.relative_to(ROOT_DIR).as_posix()
        parts.append(f"<!-- module: {rel} -->\n\n{body}")
    return "\n\n---\n\n".join(parts) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Assemble AGENTS.md from the .ai/ rule modules."
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    content = render()
    size_kib = len(content.encode("utf-8")) / 1024
    if size_kib > 30:
        print(
            f"ERROR: assembled AGENTS.md is {size_kib:.1f} KiB; Codex reads at "
            "most 32 KiB of project instructions. Trim the modules.",
            file=sys.stderr,
        )
        return 2

    current = (
        AGENTS_MD.read_text(encoding="utf-8") if AGENTS_MD.exists() else ""
    )
    if args.check:
        if current != content:
            print(
                "AGENTS.md is out of sync with .ai/ modules. "
                "Run: python dev_tools_scripts_runner.py sync-agents",
                file=sys.stderr,
            )
            return 1
        print("AGENTS.md is in sync with .ai/ modules.")
        return 0

    if current == content:
        print(f"AGENTS.md already up to date ({size_kib:.1f} KiB).")
        return 0
    AGENTS_MD.write_text(content, encoding="utf-8", newline="\n")
    print(
        f"AGENTS.md regenerated from {len(module_files())} modules ({size_kib:.1f} KiB)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
