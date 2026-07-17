from __future__ import annotations

import subprocess
import sys
from pathlib import Path


_REPO_ROOT = Path(__file__).resolve().parents[3]
_HEAVY_MODULE_PREFIXES = ("reportlab", "docx", "openpyxl", "psycopg", "pypdf")


def test_importing_cli_does_not_pull_in_heavy_rendering_or_db_libraries() -> (
    None
):
    """spec section 12: `validate` must stay usable "без дополнительных
    тяжёлых библиотек рендеринга". Run in a fresh subprocess so this
    reflects what actually happens on `import cli`, not leftover imports
    from other tests sharing the same interpreter."""
    script = (
        "import sys\n"
        "before = set(sys.modules)\n"
        "import utils.synthetic_data.cli\n"
        "after = set(sys.modules)\n"
        "new = after - before\n"
        "heavy = [m for m in new if m.split('.')[0] in "
        f"{_HEAVY_MODULE_PREFIXES!r}]\n"
        "print(','.join(sorted(heavy)))\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    heavy_modules = [m for m in result.stdout.strip().split(",") if m]
    assert not heavy_modules, (
        f"importing cli.py pulled in heavy modules: {heavy_modules}"
    )
