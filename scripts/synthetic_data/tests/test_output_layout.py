from __future__ import annotations

from pathlib import Path
from scripts.synthetic_data.core.models import FileFormat
from scripts.synthetic_data.core.output_layout import resolve_output_dir


def test_resolve_output_dir_creates_expected_subdirectories(
    output_root: Path,
) -> None:
    layout = {
        FileFormat.DOCX_COPYABLE: output_root / "docx" / "copyable",
        FileFormat.DOCX_NON_COPYABLE: output_root / "docx" / "non_copyable",
        FileFormat.DOCX_MIXED: output_root / "docx" / "mixed",
        FileFormat.PDF_COPYABLE: output_root / "pdf" / "copyable",
        FileFormat.PDF_NON_COPYABLE: output_root / "pdf" / "non_copyable",
        FileFormat.PDF_MIXED: output_root / "pdf" / "mixed",
    }

    for file_format, expected_dir in layout.items():
        resolved = resolve_output_dir(file_format, root=output_root)
        assert resolved == expected_dir
        assert resolved.is_dir()


def test_resolve_output_dir_without_create_does_not_make_directory(
    output_root: Path,
) -> None:
    target = resolve_output_dir(FileFormat.JSON, root=output_root, create=False)
    assert not target.exists()
