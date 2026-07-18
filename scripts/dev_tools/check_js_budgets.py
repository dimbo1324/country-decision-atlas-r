from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
WEB_DIR = ROOT_DIR / "apps" / "web"

# Stage 1.2 (frontend redesign) shipped /countries/[slug] at 297 kB, the
# worst route measured on 2026-07-18 after Stage 5.1-5.2 landed. The
# owner's plan asks for "current worst +10% as the ceiling, lowered in
# future waves" -- 297 rounds to 300, +10% is 330.
CEILING_KB = 330
CEILING_BYTES = CEILING_KB * 1024

_UNIT_MULTIPLIERS = {"B": 1, "KB": 1024, "MB": 1024 * 1024}

# Matches a next build route table row, e.g.:
#   "├ ƒ /[locale]/countries/[slug]                12.7 kB         297 kB"
# Next always prints two size columns (own bundle size, then First Load
# JS) as "<number> <unit>"; the header/"+ First Load JS shared by all"
# lines don't start with a tree-drawing character so this never matches
# them.
_ROUTE_LINE = re.compile(
    r"^[┌├└]\s+\S+\s+(?P<route>\S+)\s+"
    r"[\d.]+\s*[A-Za-z]+\s+"
    r"(?P<fl_num>[\d.]+)\s*(?P<fl_unit>[A-Za-z]+)\s*$"
)


@dataclass(frozen=True)
class RouteBudget:
    route: str
    first_load_bytes: int

    @property
    def first_load_kb(self) -> float:
        return self.first_load_bytes / 1024


def _to_bytes(number: str, unit: str) -> int:
    multiplier = _UNIT_MULTIPLIERS.get(unit.upper())
    if multiplier is None:
        raise ValueError(f"unrecognized size unit: {unit!r}")
    return round(float(number) * multiplier)


def parse_build_output(text: str) -> list[RouteBudget]:
    routes: list[RouteBudget] = []
    for line in text.splitlines():
        match = _ROUTE_LINE.match(line)
        if not match:
            continue
        first_load_bytes = _to_bytes(match["fl_num"], match["fl_unit"])
        routes.append(RouteBudget(match["route"], first_load_bytes))
    return routes


def run_next_build() -> str:
    result = subprocess.run(
        ["pnpm", "--filter", "@country-decision-atlas/web", "build"],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        shell=sys.platform == "win32",
    )
    output = result.stdout + result.stderr
    if result.returncode != 0:
        print(output, file=sys.stderr)
        print(
            "ERROR: next build failed, cannot check JS budgets.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fail if any apps/web route's First Load JS exceeds the fixed "
            f"ceiling ({CEILING_KB} kB)."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        help=(
            "Path to already-captured `next build` output (stdout+stderr). "
            "If omitted, runs the build itself."
        ),
    )
    args = parser.parse_args(argv)

    output = (
        args.input.read_text(encoding="utf-8")
        if args.input
        else run_next_build()
    )

    routes = parse_build_output(output)
    if not routes:
        print(
            "ERROR: no routes parsed from next build output -- Next's "
            "console table format may have changed; update the "
            "_ROUTE_LINE regex in this script.",
            file=sys.stderr,
        )
        return 2

    over_budget = [r for r in routes if r.first_load_bytes > CEILING_BYTES]

    if not over_budget:
        worst = max(routes, key=lambda r: r.first_load_bytes)
        print(
            f"JS budget OK: {len(routes)} routes checked, worst is "
            f"{worst.route} at {worst.first_load_kb:.1f} kB "
            f"(ceiling {CEILING_KB} kB)."
        )
        return 0

    print(
        f"JS budget FAILED: {len(over_budget)} route(s) exceed the "
        f"{CEILING_KB} kB First Load JS ceiling:",
        file=sys.stderr,
    )
    for route in sorted(over_budget, key=lambda r: -r.first_load_bytes):
        print(
            f"  - {route.route}: {route.first_load_kb:.1f} kB", file=sys.stderr
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
