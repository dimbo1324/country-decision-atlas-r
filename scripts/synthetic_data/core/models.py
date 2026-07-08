from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class FileFormat(StrEnum):
    JSON = "json"
    MARKDOWN = "markdown"
    EXCEL = "xlsx"
    DOCX = "docx"
    PDF_COPYABLE = "pdf-copyable"
    PDF_NON_COPYABLE = "pdf-non-copyable"

    @classmethod
    def from_alias(cls, alias: str) -> tuple[FileFormat, ...]:
        normalized = alias.strip().lower()
        if normalized == "all":
            return tuple(cls)
        if normalized == "pdf":
            return (cls.PDF_COPYABLE, cls.PDF_NON_COPYABLE)
        for member in cls:
            if member.value == normalized or member.name.lower() == normalized:
                return (member,)
        raise ValueError(f"Unknown file format alias: {alias!r}")


@dataclass(frozen=True)
class GeneratedArtifact:
    file_format: FileFormat
    path: Path
    size_bytes: int
