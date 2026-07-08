from __future__ import annotations

import random
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from scripts.synthetic_data.core.models import FileFormat
from scripts.synthetic_data.core.random_content import (
    random_paragraphs,
    random_title,
)
from scripts.synthetic_data.generators.base import BaseGenerator


_PAGE_WIDTH, _PAGE_HEIGHT = A4
_MARGIN = 20 * mm
_LINE_HEIGHT = 16
_BODY_FONT = "Helvetica"
_BODY_FONT_SIZE = 11


def _wrap_line(
    pdf_canvas: canvas.Canvas, text: str, max_width: float
) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join([*current, word])
        width = pdf_canvas.stringWidth(candidate, _BODY_FONT, _BODY_FONT_SIZE)
        if width <= max_width or not current:
            current.append(word)
        else:
            lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


class PdfCopyableGenerator(BaseGenerator):
    file_format = FileFormat.PDF_COPYABLE
    extension = "pdf"

    def _write(self, path: Path, rng: random.Random) -> None:
        pdf_canvas = canvas.Canvas(str(path), pagesize=A4)
        title = random_title(rng)
        paragraphs = random_paragraphs(rng, count=rng.randint(3, 5))
        max_width = _PAGE_WIDTH - (2 * _MARGIN)

        pdf_canvas.setFont("Helvetica-Bold", 18)
        y_offset = _PAGE_HEIGHT - _MARGIN
        pdf_canvas.drawString(_MARGIN, y_offset, title)
        y_offset -= _LINE_HEIGHT * 2

        pdf_canvas.setFont(_BODY_FONT, _BODY_FONT_SIZE)
        for paragraph in paragraphs:
            for line in _wrap_line(pdf_canvas, paragraph, max_width):
                if y_offset < _MARGIN:
                    pdf_canvas.showPage()
                    pdf_canvas.setFont(_BODY_FONT, _BODY_FONT_SIZE)
                    y_offset = _PAGE_HEIGHT - _MARGIN
                pdf_canvas.drawString(_MARGIN, y_offset, line)
                y_offset -= _LINE_HEIGHT
            y_offset -= _LINE_HEIGHT

        pdf_canvas.save()
