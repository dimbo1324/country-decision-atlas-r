from __future__ import annotations

import json
from pathlib import Path
from scripts.synthetic_data.core.document_rendering.context import (
    GeneratedDocument,
    RenderContext,
)


def render_json(ctx: RenderContext, *, output_dir: Path) -> GeneratedDocument:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{ctx.recipe.recipe_id}.json"
    marker_en, marker_local = ctx.marker_lines
    payload = {
        "synthetic_marking": {"en": marker_en, "local": marker_local},
        "recipe_id": ctx.recipe.recipe_id,
        "document_type": ctx.recipe.document_type,
        "locale": ctx.recipe.locale,
        "country": {
            "country_id": ctx.country.country_id,
            "code": ctx.country.code,
            "name": ctx.country.name,
            "archetype": ctx.country.archetype,
            "current_metrics": ctx.country.current_metrics,
            "strengths": ctx.country.strengths,
            "risks": ctx.country.risks,
        },
        "blocks": [
            {"block_id": block.block_id, "text": block.text}
            for block in ctx.recipe.blocks
        ],
    }
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    return GeneratedDocument(
        path=path,
        file_format="json",
        mode="n/a",
        locale=ctx.recipe.locale,
        country_id=ctx.country.country_id,
        recipe_id=ctx.recipe.recipe_id,
        related_artifact_ids=(ctx.country.country_id,),
        size_bytes=path.stat().st_size,
    )
