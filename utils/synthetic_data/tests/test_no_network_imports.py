from __future__ import annotations

import re
from pathlib import Path


_PACKAGE_ROOT = Path(__file__).resolve().parents[1]
_BANNED_MODULES = ("requests", "httpx", "urllib.request", "socket", "aiohttp")
_IMPORT_PATTERN = re.compile(
    r"^\s*(?:import|from)\s+("
    + "|".join(re.escape(m) for m in _BANNED_MODULES)
    + r")\b"
)


def _python_files() -> list[Path]:
    return sorted(_PACKAGE_ROOT.rglob("*.py"))


def test_no_network_client_imports_anywhere_in_synthetic_data() -> None:
    """The pipeline's autonomy (spec section 4/14.3: "без сетевых запросов")
    currently holds only because no code happens to import a networking
    library — this test makes that an enforced invariant instead of an
    accident, the same pattern the project already uses for the
    `::text = %s` ban in repositories."""
    violations: list[str] = []
    for path in _python_files():
        text = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), start=1):
            match = _IMPORT_PATTERN.match(line)
            if match:
                violations.append(
                    f"{path.relative_to(_PACKAGE_ROOT)}:{line_number}: "
                    f"imports banned module {match.group(1)!r}"
                )
    assert not violations, "\n".join(violations)


def test_psycopg_is_only_imported_by_the_explicit_sql_seam() -> None:
    """`psycopg` is allowed only in the two modules that make up the
    explicit, `--confirm`-gated SQL feature: `sql_fixture.py` (offline
    text escaping, no connection) and `sql_loader.py` (the actual, gated
    connection). It should not spread beyond that seam."""
    allowed = {
        _PACKAGE_ROOT / "core" / "sql_fixture.py",
        _PACKAGE_ROOT / "core" / "sql_loader.py",
    }
    pattern = re.compile(r"^\s*(?:import|from)\s+psycopg\b")
    violations: list[str] = []
    for path in _python_files():
        if path in allowed:
            continue
        text = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if pattern.match(line):
                violations.append(
                    f"{path.relative_to(_PACKAGE_ROOT)}:{line_number}: "
                    "imports psycopg outside core/sql_loader.py"
                )
    assert not violations, "\n".join(violations)
