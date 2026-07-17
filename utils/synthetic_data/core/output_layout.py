from __future__ import annotations

from pathlib import Path
from utils.synthetic_data.core.models import FileFormat
from utils.synthetic_data.core.paths import DEFAULT_OUTPUT_DATA_ROOT


_FORMAT_SUBDIRECTORIES: dict[FileFormat, Path] = {
    FileFormat.JSON: Path("json"),
    FileFormat.MARKDOWN: Path("markdown"),
    FileFormat.EXCEL: Path("xlsx"),
    FileFormat.DOCX_COPYABLE: Path("docx/copyable"),
    FileFormat.DOCX_NON_COPYABLE: Path("docx/non_copyable"),
    FileFormat.DOCX_MIXED: Path("docx/mixed"),
    FileFormat.PDF_COPYABLE: Path("pdf/copyable"),
    FileFormat.PDF_NON_COPYABLE: Path("pdf/non_copyable"),
    FileFormat.PDF_MIXED: Path("pdf/mixed"),
}


def resolve_output_dir(
    file_format: FileFormat,
    *,
    root: Path = DEFAULT_OUTPUT_DATA_ROOT,
    create: bool = True,
) -> Path:
    target_dir = root / _FORMAT_SUBDIRECTORIES[file_format]
    if create:
        target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir
