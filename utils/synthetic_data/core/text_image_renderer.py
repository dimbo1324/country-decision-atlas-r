from __future__ import annotations

from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont


DEFAULT_PAGE_SIZE_PX = (1240, 1754)
DEFAULT_MARGIN_PX = 90
DEFAULT_FONT_SIZE = 28
DEFAULT_LINE_SPACING = 12


@dataclass(frozen=True)
class PageLayout:
    page_size: tuple[int, int] = DEFAULT_PAGE_SIZE_PX
    margin: int = DEFAULT_MARGIN_PX
    font_size: int = DEFAULT_FONT_SIZE
    line_spacing: int = DEFAULT_LINE_SPACING


DEFAULT_PAGE_LAYOUT = PageLayout()

type _Font = ImageFont.FreeTypeFont | ImageFont.ImageFont


def _measurement_draw() -> ImageDraw.ImageDraw:
    return ImageDraw.Draw(Image.new("RGB", (1, 1)))


def _wrap_line(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: _Font,
    max_width: int,
) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join([*current, word])
        bbox = draw.textbbox((0, 0), candidate, font=font)
        width = bbox[2] - bbox[0]
        if width <= max_width or not current:
            current.append(word)
        else:
            lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def render_paragraphs_to_pages(
    paragraphs: list[str],
    *,
    layout: PageLayout = DEFAULT_PAGE_LAYOUT,
    font_path: str | None = None,
) -> list[Image.Image]:
    font: _Font = (
        ImageFont.truetype(font_path, size=layout.font_size)
        if font_path
        else ImageFont.load_default(size=layout.font_size)
    )
    draw = _measurement_draw()
    max_width = layout.page_size[0] - (layout.margin * 2)
    line_height = layout.font_size + layout.line_spacing

    lines: list[str] = []
    for paragraph in paragraphs:
        lines.extend(_wrap_line(draw, paragraph, font, max_width))
        lines.append("")

    usable_height = layout.page_size[1] - (layout.margin * 2)
    lines_per_page = max(1, usable_height // line_height)

    pages: list[Image.Image] = []
    for start in range(0, len(lines), lines_per_page):
        page_image = Image.new("RGB", layout.page_size, color="white")
        page_draw = ImageDraw.Draw(page_image)
        y_offset = layout.margin
        for line in lines[start : start + lines_per_page]:
            page_draw.text(
                (layout.margin, y_offset), line, font=font, fill="black"
            )
            y_offset += line_height
        pages.append(page_image)

    if not pages:
        pages.append(Image.new("RGB", layout.page_size, color="white"))
    return pages


def render_text_snippet(
    text: str,
    *,
    font_size: int = 22,
    padding: int = 16,
    max_width_px: int = 900,
    font_path: str | None = None,
) -> Image.Image:
    font: _Font = (
        ImageFont.truetype(font_path, size=font_size)
        if font_path
        else ImageFont.load_default(size=font_size)
    )
    draw = _measurement_draw()
    lines = _wrap_line(draw, text, font, max_width_px - (padding * 2))
    line_height = font_size + (padding // 2)
    content_width = max(
        (int(draw.textbbox((0, 0), line, font=font)[2]) for line in lines),
        default=0,
    )
    image_width = content_width + (padding * 2)
    image_height = (line_height * len(lines)) + (padding * 2)

    image = Image.new("RGB", (image_width, image_height), color="white")
    image_draw = ImageDraw.Draw(image)
    y_offset = padding
    for line in lines:
        image_draw.text((padding, y_offset), line, font=font, fill="black")
        y_offset += line_height
    return image
