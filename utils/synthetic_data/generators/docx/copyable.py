from __future__ import annotations

from docx import Document
from pathlib import Path
from utils.synthetic_data.core.models import FileFormat
from utils.synthetic_data.core.random_content import RandomContentFactory
from utils.synthetic_data.generators.base import BaseGenerator


class DocxCopyableGenerator(BaseGenerator):
    file_format = FileFormat.DOCX_COPYABLE
    extension = "docx"

    def _write(self, path: Path, content: RandomContentFactory) -> None:
        document = Document()
        document.add_heading(content.title(), level=1)
        for paragraph in content.paragraphs(count=content.randint(3, 5)):
            document.add_paragraph(paragraph)
        document.save(str(path))
