from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from scripts.synthetic_data.core.document_rendering.context import (
    GeneratedDocument,
)
from scripts.synthetic_data.core.world_models import SyntheticWorld
from typing import cast


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _file_entry(path: Path, *, dataset_dir: Path) -> dict[str, object]:
    return {
        "path": path.relative_to(dataset_dir).as_posix(),
        "format": path.suffix.lstrip("."),
        "mode": "n/a",
        "locale": None,
        "size_bytes": path.stat().st_size,
        "sha256": _sha256(path),
        "related_artifacts": [],
    }


def _document_entry(
    document: GeneratedDocument, *, dataset_dir: Path
) -> dict[str, object]:
    return {
        "path": document.path.relative_to(dataset_dir).as_posix(),
        "format": document.file_format,
        "mode": document.mode,
        "locale": document.locale,
        "size_bytes": document.size_bytes,
        "sha256": _sha256(document.path),
        "related_artifacts": list(document.related_artifact_ids),
    }


def build_manifest(
    *,
    world: SyntheticWorld,
    dataset_dir: Path,
    documents: list[GeneratedDocument],
    world_level_files: list[Path],
) -> dict[str, object]:
    """Build the manifest payload for section 10: every artifact, its
    format, size, checksum, locale, and related entities, so the dataset
    directory is auditable without re-running the generator."""
    entries = [
        _file_entry(path, dataset_dir=dataset_dir) for path in world_level_files
    ] + [_document_entry(doc, dataset_dir=dataset_dir) for doc in documents]
    entries.sort(key=lambda entry: cast(str, entry["path"]))

    return {
        "dataset_id": world.metadata.dataset_id,
        "schema_version": world.metadata.schema_version,
        "generator_version": world.metadata.generator_version,
        "seed": world.metadata.seed,
        "profile": world.metadata.profile,
        "supported_locales": list(world.metadata.supported_locales),
        "fictional_notice": world.metadata.fictional_notice,
        "manifest_generated_at": datetime.now(UTC)
        .isoformat()
        .replace("+00:00", "Z"),
        "artifact_count": len(entries),
        "artifacts": entries,
    }


def write_manifest(manifest: dict[str, object], *, dataset_dir: Path) -> Path:
    path = dataset_dir / "manifest.json"
    path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    return path


def write_generation_summary(
    *,
    world: SyntheticWorld,
    manifest: dict[str, object],
    dataset_dir: Path,
) -> Path:
    path = dataset_dir / "reports" / "generation_summary.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    format_counts: dict[str, int] = {}
    locale_counts: dict[str, int] = {}
    artifacts = cast(list[dict[str, object]], manifest["artifacts"])
    for entry in artifacts:
        file_format = cast(str, entry["format"])
        format_counts[file_format] = format_counts.get(file_format, 0) + 1
        locale = entry.get("locale")
        if isinstance(locale, str):
            locale_counts[locale] = locale_counts.get(locale, 0) + 1

    lines = [
        f"# Synthetic dataset {world.metadata.dataset_id}",
        "",
        f"- profile: `{world.metadata.profile}`",
        f"- seed: `{world.metadata.seed}`",
        f"- countries: {len(world.countries)}",
        f"- scenarios: {len(world.scenarios)}",
        f"- document recipes: {len(world.document_recipes)}",
        f"- supported locales: {len(world.metadata.supported_locales)}",
        f"- total artifacts: {manifest['artifact_count']}",
        "",
        "## Artifacts by format",
        "",
    ]
    for file_format, count in sorted(format_counts.items()):
        lines.append(f"- {file_format}: {count}")
    lines.append("")
    lines.append("## Artifacts by locale")
    lines.append("")
    for locale, count in sorted(locale_counts.items()):
        lines.append(f"- {locale}: {count}")
    lines.append("")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
