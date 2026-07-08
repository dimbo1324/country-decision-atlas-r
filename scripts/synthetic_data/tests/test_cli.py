from __future__ import annotations

from pathlib import Path
from scripts.synthetic_data import cli
from scripts.synthetic_data.core.models import FileFormat


def test_dry_run_does_not_create_files(output_root: Path) -> None:
    exit_code = cli.main(
        [
            "--formats",
            "json,markdown",
            "--output-root",
            str(output_root),
            "--dry-run",
        ]
    )
    assert exit_code == 0
    assert not output_root.exists()


def test_generate_writes_expected_layout(output_root: Path) -> None:
    exit_code = cli.main(
        [
            "--formats",
            "all",
            "--seed",
            "99",
            "--output-root",
            str(output_root),
        ]
    )
    assert exit_code == 0

    expected_dirs = {
        FileFormat.JSON: output_root / "json",
        FileFormat.MARKDOWN: output_root / "markdown",
        FileFormat.EXCEL: output_root / "xlsx",
        FileFormat.DOCX: output_root / "docx",
        FileFormat.PDF_COPYABLE: output_root / "pdf" / "copyable",
        FileFormat.PDF_NON_COPYABLE: output_root / "pdf" / "non_copyable",
    }
    for directory in expected_dirs.values():
        assert len(list(directory.glob("sample_*"))) == 1


def test_unknown_format_returns_error(output_root: Path) -> None:
    exit_code = cli.main(
        ["--formats", "not-a-format", "--output-root", str(output_root)]
    )
    assert exit_code == 2


def test_invalid_count_returns_error(output_root: Path) -> None:
    exit_code = cli.main(
        [
            "--formats",
            "json",
            "--count",
            "0",
            "--output-root",
            str(output_root),
        ]
    )
    assert exit_code == 2
