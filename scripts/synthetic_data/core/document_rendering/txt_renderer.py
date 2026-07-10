from __future__ import annotations

from pathlib import Path
from scripts.synthetic_data.core.document_rendering.context import (
    GeneratedDocument,
    RenderContext,
)


def render_txt(ctx: RenderContext, *, output_dir: Path) -> GeneratedDocument:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{ctx.recipe.recipe_id}.txt"
    marker_en, marker_local = ctx.marker_lines
    lines = [marker_en, marker_local, "", ctx.country.name, ""]
    for block in ctx.recipe.blocks:
        lines.append(block.text)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return GeneratedDocument(
        path=path,
        file_format="txt",
        mode="n/a",
        locale=ctx.recipe.locale,
        country_id=ctx.country.country_id,
        recipe_id=ctx.recipe.recipe_id,
        related_artifact_ids=(ctx.country.country_id,),
        size_bytes=path.stat().st_size,
    )
