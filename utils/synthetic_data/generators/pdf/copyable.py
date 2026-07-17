from __future__ import annotations

from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from utils.synthetic_data.core.models import FileFormat
from utils.synthetic_data.core.random_content import RandomContentFactory
from utils.synthetic_data.generators.base import BaseGenerator
from utils.synthetic_data.generators.pdf._reportlab_text import (
    draw_text_page,
)


class PdfCopyableGenerator(BaseGenerator):
    file_format = FileFormat.PDF_COPYABLE
    extension = "pdf"

    def _write(self, path: Path, content: RandomContentFactory) -> None:
        pdf_canvas = canvas.Canvas(str(path), pagesize=A4)
        title = content.title()
        paragraphs = content.paragraphs(count=content.randint(3, 5))
        draw_text_page(pdf_canvas, title, paragraphs)
        pdf_canvas.save()
