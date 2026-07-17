from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class FileFormat(StrEnum):
    JSON = "json"
    MARKDOWN = "markdown"
    EXCEL = "xlsx"
    DOCX_COPYABLE = "docx-copyable"
    DOCX_NON_COPYABLE = "docx-non-copyable"
    DOCX_MIXED = "docx-mixed"
    PDF_COPYABLE = "pdf-copyable"
    PDF_NON_COPYABLE = "pdf-non-copyable"
    PDF_MIXED = "pdf-mixed"

    @classmethod
    def from_alias(cls, alias: str) -> tuple[FileFormat, ...]:
        normalized = alias.strip().lower()
        if normalized == "all":
            return tuple(cls)
        if normalized == "docx":
            return (cls.DOCX_COPYABLE, cls.DOCX_NON_COPYABLE, cls.DOCX_MIXED)
        if normalized == "pdf":
            return (cls.PDF_COPYABLE, cls.PDF_NON_COPYABLE, cls.PDF_MIXED)
        for member in cls:
            if member.value == normalized or member.name.lower() == normalized:
                return (member,)
        raise ValueError(f"Unknown file format alias: {alias!r}")


@dataclass(frozen=True)
class GeneratedArtifact:
    file_format: FileFormat
    path: Path
    size_bytes: int
