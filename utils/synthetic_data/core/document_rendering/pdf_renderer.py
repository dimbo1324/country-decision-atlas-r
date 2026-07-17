from __future__ import annotations

from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from utils.synthetic_data.core.document_rendering.context import (
    GeneratedDocument,
    RenderContext,
)
from utils.synthetic_data.core.font_registry import (
    ScriptFont,
    font_for_script,
)
from utils.synthetic_data.core.text_image_renderer import (
    render_paragraphs_to_pages,
)
from utils.synthetic_data.core.text_shaping import (
    shape_for_display,
    wrap_text,
)


PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 20 * mm
LINE_HEIGHT = 16
BODY_FONT_SIZE = 11
TITLE_FONT_SIZE = 16
MARKER_FONT_SIZE = 8

_registered_fonts: set[str] = set()


def _ensure_registered(font: ScriptFont) -> None:
    if font.font_name not in _registered_fonts:
        pdfmetrics.registerFont(TTFont(font.font_name, str(font.file_path)))
        _registered_fonts.add(font.font_name)


def _draw_line(
    pdf_canvas: canvas.Canvas,
    line: str,
    *,
    font_name: str,
    font_size: float,
    y_offset: float,
    is_rtl: bool,
) -> None:
    display_line = shape_for_display(line, is_rtl=is_rtl)
    if is_rtl:
        width = pdf_canvas.stringWidth(display_line, font_name, font_size)
        pdf_canvas.drawString(
            PAGE_WIDTH - MARGIN - width, y_offset, display_line
        )
    else:
        pdf_canvas.drawString(MARGIN, y_offset, display_line)


def _draw_marker(
    pdf_canvas: canvas.Canvas,
    *,
    marker_en: str,
    marker_local: str,
    latin_font: ScriptFont,
    local_font: ScriptFont,
    is_rtl: bool,
) -> None:
    pdf_canvas.setFont(latin_font.font_name, MARKER_FONT_SIZE)
    pdf_canvas.drawString(MARGIN, PAGE_HEIGHT - 10 * mm, marker_en)
    pdf_canvas.setFont(local_font.font_name, MARKER_FONT_SIZE)
    _draw_line(
        pdf_canvas,
        marker_local,
        font_name=local_font.font_name,
        font_size=MARKER_FONT_SIZE,
        y_offset=PAGE_HEIGHT - 14 * mm,
        is_rtl=is_rtl,
    )


def _draw_document_body(pdf_canvas: canvas.Canvas, ctx: RenderContext) -> None:
    local_font = font_for_script(ctx.script)
    latin_font = font_for_script("Latin")
    _ensure_registered(local_font)
    _ensure_registered(latin_font)
    marker_en, marker_local = ctx.marker_lines

    def new_page() -> float:
        _draw_marker(
            pdf_canvas,
            marker_en=marker_en,
            marker_local=marker_local,
            latin_font=latin_font,
            local_font=local_font,
            is_rtl=ctx.is_rtl,
        )
        return float(PAGE_HEIGHT - 22 * mm)

    y_offset = new_page()

    pdf_canvas.setFont(latin_font.font_name, TITLE_FONT_SIZE)
    pdf_canvas.drawString(MARGIN, y_offset, ctx.country.name)
    y_offset -= LINE_HEIGHT * 2

    pdf_canvas.setFont(local_font.font_name, BODY_FONT_SIZE)
    max_width = PAGE_WIDTH - (2 * MARGIN)
    for block in ctx.recipe.blocks:
        lines = wrap_text(
            block.text,
            script=ctx.script,
            measure_width=lambda candidate: pdf_canvas.stringWidth(
                candidate, local_font.font_name, BODY_FONT_SIZE
            ),
            max_width=max_width,
        )
        for line in lines:
            if y_offset < MARGIN:
                pdf_canvas.showPage()
                y_offset = new_page()
                pdf_canvas.setFont(local_font.font_name, BODY_FONT_SIZE)
            _draw_line(
                pdf_canvas,
                line,
                font_name=local_font.font_name,
                font_size=BODY_FONT_SIZE,
                y_offset=y_offset,
                is_rtl=ctx.is_rtl,
            )
            y_offset -= LINE_HEIGHT
        y_offset -= LINE_HEIGHT


def render_pdf_copyable(
    ctx: RenderContext, *, output_dir: Path
) -> GeneratedDocument:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{ctx.recipe.recipe_id}.pdf"
    pdf_canvas = canvas.Canvas(str(path), pagesize=A4)
    _draw_document_body(pdf_canvas, ctx)
    pdf_canvas.save()
    return GeneratedDocument(
        path=path,
        file_format="pdf",
        mode="copyable",
        locale=ctx.recipe.locale,
        country_id=ctx.country.country_id,
        recipe_id=ctx.recipe.recipe_id,
        related_artifact_ids=(ctx.country.country_id,),
        size_bytes=path.stat().st_size,
    )


def render_pdf_non_copyable(
    ctx: RenderContext, *, output_dir: Path
) -> GeneratedDocument:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{ctx.recipe.recipe_id}.pdf"
    font = font_for_script(ctx.script)
    marker_en, marker_local = ctx.marker_lines
    paragraphs = [
        marker_en,
        shape_for_display(marker_local, is_rtl=ctx.is_rtl),
        ctx.country.name,
        *(
            shape_for_display(block.text, is_rtl=ctx.is_rtl)
            for block in ctx.recipe.blocks
        ),
    ]
    pages = render_paragraphs_to_pages(
        paragraphs, font_path=str(font.file_path)
    )
    pdf_canvas = canvas.Canvas(str(path), pagesize=A4)
    for page_image in pages:
        pdf_canvas.drawImage(
            ImageReader(page_image),
            0,
            0,
            width=PAGE_WIDTH,
            height=PAGE_HEIGHT,
        )
        pdf_canvas.showPage()
    pdf_canvas.save()
    return GeneratedDocument(
        path=path,
        file_format="pdf",
        mode="non_copyable",
        locale=ctx.recipe.locale,
        country_id=ctx.country.country_id,
        recipe_id=ctx.recipe.recipe_id,
        related_artifact_ids=(ctx.country.country_id,),
        size_bytes=path.stat().st_size,
    )


def render_pdf_mixed(
    ctx: RenderContext, *, output_dir: Path
) -> GeneratedDocument:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{ctx.recipe.recipe_id}.pdf"
    pdf_canvas = canvas.Canvas(str(path), pagesize=A4)
    _draw_document_body(pdf_canvas, ctx)
    pdf_canvas.showPage()

    font = font_for_script(ctx.script)
    scanned_text = shape_for_display(
        ctx.recipe.blocks[-1].text, is_rtl=ctx.is_rtl
    )
    pages = render_paragraphs_to_pages(
        [scanned_text], font_path=str(font.file_path)
    )
    pdf_canvas.drawImage(
        ImageReader(pages[0]), 0, 0, width=PAGE_WIDTH, height=PAGE_HEIGHT
    )
    pdf_canvas.showPage()
    pdf_canvas.save()
    return GeneratedDocument(
        path=path,
        file_format="pdf",
        mode="mixed",
        locale=ctx.recipe.locale,
        country_id=ctx.country.country_id,
        recipe_id=ctx.recipe.recipe_id,
        related_artifact_ids=(ctx.country.country_id,),
        size_bytes=path.stat().st_size,
    )
