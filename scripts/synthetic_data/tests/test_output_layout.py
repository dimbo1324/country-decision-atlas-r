from __future__ import annotations

from pathlib import Path
from scripts.synthetic_data.core.models import FileFormat
from scripts.synthetic_data.core.output_layout import resolve_output_dir


def test_resolve_output_dir_creates_expected_subdirectories(
    output_root: Path,
) -> None:
    pdf_copyable_dir = resolve_output_dir(
        FileFormat.PDF_COPYABLE, root=output_root
    )
    pdf_non_copyable_dir = resolve_output_dir(
        FileFormat.PDF_NON_COPYABLE, root=output_root
    )

    assert pdf_copyable_dir == output_root / "pdf" / "copyable"
    assert pdf_non_copyable_dir == output_root / "pdf" / "non_copyable"
    assert pdf_copyable_dir.is_dir()
    assert pdf_non_copyable_dir.is_dir()


def test_resolve_output_dir_without_create_does_not_make_directory(
    output_root: Path,
) -> None:
    target = resolve_output_dir(FileFormat.JSON, root=output_root, create=False)
    assert not target.exists()
