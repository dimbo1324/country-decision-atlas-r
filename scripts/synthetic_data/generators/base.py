from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from pathlib import Path
from scripts.synthetic_data.core.models import FileFormat, GeneratedArtifact
from scripts.synthetic_data.core.random_content import RandomContentFactory


class BaseGenerator(ABC):
    file_format: FileFormat
    extension: str

    def generate(
        self, *, output_dir: Path, content: RandomContentFactory
    ) -> GeneratedArtifact:
        target_path = output_dir / self._build_filename()
        self._write(target_path, content)
        return GeneratedArtifact(
            file_format=self.file_format,
            path=target_path,
            size_bytes=target_path.stat().st_size,
        )

    def _build_filename(self) -> str:
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%f")
        unique_suffix = uuid.uuid4().hex[:8]
        return f"sample_{timestamp}_{unique_suffix}.{self.extension}"

    @abstractmethod
    def _write(self, path: Path, content: RandomContentFactory) -> None: ...
