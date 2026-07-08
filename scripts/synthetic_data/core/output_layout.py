from __future__ import annotations

from pathlib import Path
from scripts.synthetic_data.core.models import FileFormat


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SYNTHETIC_DATA_ROOT = REPO_ROOT / "docs" / "synthetic_data"

_FORMAT_SUBDIRECTORIES: dict[FileFormat, Path] = {
    FileFormat.JSON: Path("json"),
    FileFormat.MARKDOWN: Path("markdown"),
    FileFormat.EXCEL: Path("xlsx"),
    FileFormat.DOCX: Path("docx"),
    FileFormat.PDF_COPYABLE: Path("pdf/copyable"),
    FileFormat.PDF_NON_COPYABLE: Path("pdf/non_copyable"),
}


def resolve_output_dir(
    file_format: FileFormat,
    *,
    root: Path = DEFAULT_SYNTHETIC_DATA_ROOT,
    create: bool = True,
) -> Path:
    target_dir = root / _FORMAT_SUBDIRECTORIES[file_format]
    if create:
        target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir
