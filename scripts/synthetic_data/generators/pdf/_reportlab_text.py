from __future__ import annotations

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 20 * mm
LINE_HEIGHT = 16
BODY_FONT = "Helvetica"
BODY_FONT_SIZE = 11
TITLE_FONT = "Helvetica-Bold"
TITLE_FONT_SIZE = 18


def wrap_line(
    pdf_canvas: canvas.Canvas, text: str, max_width: float
) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join([*current, word])
        width = pdf_canvas.stringWidth(candidate, BODY_FONT, BODY_FONT_SIZE)
        if width <= max_width or not current:
            current.append(word)
        else:
            lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def draw_text_page(
    pdf_canvas: canvas.Canvas, title: str, paragraphs: list[str]
) -> None:
    max_width = PAGE_WIDTH - (2 * MARGIN)

    pdf_canvas.setFont(TITLE_FONT, TITLE_FONT_SIZE)
    y_offset = PAGE_HEIGHT - MARGIN
    pdf_canvas.drawString(MARGIN, y_offset, title)
    y_offset -= LINE_HEIGHT * 2

    pdf_canvas.setFont(BODY_FONT, BODY_FONT_SIZE)
    for paragraph in paragraphs:
        for line in wrap_line(pdf_canvas, paragraph, max_width):
            if y_offset < MARGIN:
                pdf_canvas.showPage()
                pdf_canvas.setFont(BODY_FONT, BODY_FONT_SIZE)
                y_offset = PAGE_HEIGHT - MARGIN
            pdf_canvas.drawString(MARGIN, y_offset, line)
            y_offset -= LINE_HEIGHT
        y_offset -= LINE_HEIGHT
