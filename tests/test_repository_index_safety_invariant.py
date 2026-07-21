"""Invariant: repository SQL never casts an indexed column to text for equality.

`column::text = %s` defeats the b-tree index on `column` (the cast is applied to
every row before compare), forcing a sequential scan. The correct form casts the
parameter instead: `column = %s::uuid`. A hardening-audit finding, P0-1.
"""

import re
from pathlib import Path


REPOSITORIES_DIR = Path("apps/api/app/repositories")
FORBIDDEN_CAST_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_.]*::text\s*=\s*%s")


def test_repositories_never_cast_column_to_text_for_equality() -> None:
    violations: list[str] = []
    for module_path in REPOSITORIES_DIR.rglob("*.py"):
        source = module_path.read_text(encoding="utf-8")
        for match in FORBIDDEN_CAST_PATTERN.finditer(source):
            line_number = source.count("\n", 0, match.start()) + 1
            violations.append(
                f"{module_path.as_posix()}:{line_number}: {match.group(0)!r}"
            )
    assert not violations, (
        "Found index-defeating '<column>::text = %s' cast(s). "
        "Cast the parameter instead: '<column> = %s::uuid'.\n"
        + "\n".join(violations)
    )
