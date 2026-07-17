from __future__ import annotations

import json
from pathlib import Path
from utils.synthetic_data import cli
from utils.synthetic_data.core.models import FileFormat


_SAMPLE_INPUT_DATA = {
    "words": ["alpha", "bravo", "charlie", "delta", "echo"],
    "headers": ["Overview", "Summary", "Notes"],
}


def _write_input_file(tmp_path: Path) -> Path:
    input_file = tmp_path / "data.json"
    input_file.write_text(json.dumps(_SAMPLE_INPUT_DATA), encoding="utf-8")
    return input_file


def test_dry_run_does_not_create_files(
    output_root: Path, tmp_path: Path
) -> None:
    exit_code = cli.main(
        [
            "--formats",
            "json,markdown",
            "--input-file",
            str(_write_input_file(tmp_path)),
            "--output-root",
            str(output_root),
            "--dry-run",
        ]
    )
    assert exit_code == 0
    assert not output_root.exists()


def test_generate_writes_expected_layout(
    output_root: Path, tmp_path: Path
) -> None:
    exit_code = cli.main(
        [
            "--formats",
            "all",
            "--seed",
            "99",
            "--input-file",
            str(_write_input_file(tmp_path)),
            "--output-root",
            str(output_root),
        ]
    )
    assert exit_code == 0

    expected_dirs = {
        FileFormat.JSON: output_root / "json",
        FileFormat.MARKDOWN: output_root / "markdown",
        FileFormat.EXCEL: output_root / "xlsx",
        FileFormat.DOCX_COPYABLE: output_root / "docx" / "copyable",
        FileFormat.DOCX_NON_COPYABLE: output_root / "docx" / "non_copyable",
        FileFormat.DOCX_MIXED: output_root / "docx" / "mixed",
        FileFormat.PDF_COPYABLE: output_root / "pdf" / "copyable",
        FileFormat.PDF_NON_COPYABLE: output_root / "pdf" / "non_copyable",
        FileFormat.PDF_MIXED: output_root / "pdf" / "mixed",
    }
    for directory in expected_dirs.values():
        assert len(list(directory.glob("sample_*"))) == 1


def test_unknown_format_returns_error(
    output_root: Path, tmp_path: Path
) -> None:
    exit_code = cli.main(
        [
            "--formats",
            "not-a-format",
            "--input-file",
            str(_write_input_file(tmp_path)),
            "--output-root",
            str(output_root),
        ]
    )
    assert exit_code == 2


def test_invalid_count_returns_error(output_root: Path, tmp_path: Path) -> None:
    exit_code = cli.main(
        [
            "--formats",
            "json",
            "--count",
            "0",
            "--input-file",
            str(_write_input_file(tmp_path)),
            "--output-root",
            str(output_root),
        ]
    )
    assert exit_code == 2


def test_missing_input_file_returns_error(
    output_root: Path, tmp_path: Path
) -> None:
    missing_path = tmp_path / "does-not-exist.json"
    exit_code = cli.main(
        [
            "--formats",
            "json",
            "--input-file",
            str(missing_path),
            "--output-root",
            str(output_root),
        ]
    )
    assert exit_code == 2
