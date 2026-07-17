from __future__ import annotations

import json
from collections.abc import Collection
from dataclasses import dataclass
from pathlib import Path
from utils.synthetic_data.archive.zip_archiver import (
    create_zip_archive,
    write_archive_checksum,
)
from utils.synthetic_data.core.artifact_validation import (
    validate_generated_documents,
)
from utils.synthetic_data.core.dashboard import render_dashboard
from utils.synthetic_data.core.document_formats import ALL_DOCUMENT_FORMATS
from utils.synthetic_data.core.document_rendering.context import (
    GeneratedDocument,
    RenderContext,
)
from utils.synthetic_data.core.document_rendering.docx_renderer import (
    render_docx_copyable,
    render_docx_mixed,
    render_docx_non_copyable,
)
from utils.synthetic_data.core.document_rendering.json_renderer import (
    render_json,
)
from utils.synthetic_data.core.document_rendering.pdf_renderer import (
    render_pdf_copyable,
    render_pdf_mixed,
    render_pdf_non_copyable,
)
from utils.synthetic_data.core.document_rendering.txt_renderer import (
    render_txt,
)
from utils.synthetic_data.core.document_rendering.xlsx_renderer import (
    render_xlsx,
)
from utils.synthetic_data.core.locale_corpus import LocaleCorpus
from utils.synthetic_data.core.manifest import (
    build_manifest,
    write_generation_summary,
    write_manifest,
    write_manifest_checksum,
)
from utils.synthetic_data.core.sql_fixture import (
    build_cleanup_sql,
    build_seed_sql,
)
from utils.synthetic_data.core.world_models import SyntheticWorld


_DOCX_RENDERERS = {
    "copyable": render_docx_copyable,
    "non_copyable": render_docx_non_copyable,
    "mixed": render_docx_mixed,
}
_PDF_RENDERERS = {
    "copyable": render_pdf_copyable,
    "non_copyable": render_pdf_non_copyable,
    "mixed": render_pdf_mixed,
}


def render_dataset_documents(
    *,
    world: SyntheticWorld,
    locale_corpus: LocaleCorpus,
    dataset_dir: Path,
    formats: Collection[str] = ALL_DOCUMENT_FORMATS,
) -> list[GeneratedDocument]:
    """Render every document recipe into `documents/<locale>/<format>/
    [<mode>]/` (spec section 10), reading only from the already-built
    canonical `world` and its resolved recipes."""
    documents: list[GeneratedDocument] = []
    countries_by_id = {
        country.country_id: country for country in world.countries
    }
    for recipe in world.document_recipes:
        country = countries_by_id[recipe.country_id]
        text_pack = locale_corpus.by_locale(recipe.locale)
        ctx = RenderContext(
            world=world, recipe=recipe, country=country, text_pack=text_pack
        )
        locale_dir = dataset_dir / "documents" / recipe.locale
        if "json" in formats:
            documents.append(render_json(ctx, output_dir=locale_dir / "json"))
        if "txt" in formats:
            documents.append(render_txt(ctx, output_dir=locale_dir / "txt"))
        if "xlsx" in formats:
            documents.append(render_xlsx(ctx, output_dir=locale_dir / "xlsx"))
        if "docx" in formats:
            for mode, renderer in _DOCX_RENDERERS.items():
                documents.append(
                    renderer(ctx, output_dir=locale_dir / "docx" / mode)
                )
        if "pdf" in formats:
            for mode, renderer in _PDF_RENDERERS.items():
                documents.append(
                    renderer(ctx, output_dir=locale_dir / "pdf" / mode)
                )
    return documents


def discover_existing_documents(
    *, world: SyntheticWorld, dataset_dir: Path
) -> list[GeneratedDocument]:
    """Reconstruct `GeneratedDocument` entries for files already rendered
    on disk, without rendering anything — lets `package` repackage an
    existing dataset's manifest/ZIP cheaply instead of re-running every
    renderer."""
    documents_dir = dataset_dir / "documents"
    if not documents_dir.exists():
        return []
    recipes_by_id = {
        recipe.recipe_id: recipe for recipe in world.document_recipes
    }
    documents: list[GeneratedDocument] = []
    for path in sorted(documents_dir.rglob("*")):
        if not path.is_file():
            continue
        recipe = recipes_by_id.get(path.stem)
        if recipe is None:
            continue
        parts = path.relative_to(documents_dir).parts
        locale, file_format = parts[0], parts[1]
        mode = parts[2] if file_format in ("docx", "pdf") else "n/a"
        documents.append(
            GeneratedDocument(
                path=path,
                file_format=file_format,
                mode=mode,
                locale=locale,
                country_id=recipe.country_id,
                recipe_id=recipe.recipe_id,
                related_artifact_ids=(recipe.country_id,),
                size_bytes=path.stat().st_size,
            )
        )
    return documents


@dataclass(frozen=True)
class PackageResult:
    manifest_path: Path
    summary_path: Path
    validation_report_path: Path
    dashboard_path: Path
    manifest_checksum_path: Path
    zip_path: Path
    package_checksum_path: Path
    artifact_errors: tuple[str, ...]


def package_dataset(
    *,
    world: SyntheticWorld,
    world_errors: tuple[str, ...],
    dataset_dir: Path,
    documents: list[GeneratedDocument],
    extra_files: Collection[Path] = (),
) -> PackageResult:
    """Validate rendered artifacts, then write manifest, validation
    report, human summary, and the ZIP package (spec section 23, stage 5,
    item 5). `extra_files` folds in artifacts this function doesn't know
    how to render itself -- currently the website layer's rendered pages
    plus its graph.json/source_pages.json (utils/synthetic_data/web/)."""
    artifact_errors = tuple(validate_generated_documents(documents))
    all_errors = world_errors + artifact_errors

    sql_dir = dataset_dir / "sql"
    sql_dir.mkdir(parents=True, exist_ok=True)
    seed_sql_path = sql_dir / "seed_synthetic_world.sql"
    cleanup_sql_path = sql_dir / "cleanup_synthetic_world.sql"
    seed_sql_path.write_text(build_seed_sql(world), encoding="utf-8")
    cleanup_sql_path.write_text(build_cleanup_sql(world), encoding="utf-8")

    world_level_files = [
        path
        for path in (
            dataset_dir / "canonical" / "synthetic_world.json",
            dataset_dir / "canonical" / "scenarios.json",
            seed_sql_path,
            cleanup_sql_path,
            *extra_files,
        )
        if path.exists()
    ]
    manifest = build_manifest(
        world=world,
        dataset_dir=dataset_dir,
        documents=documents,
        world_level_files=world_level_files,
    )
    manifest_path = write_manifest(manifest, dataset_dir=dataset_dir)
    summary_path = write_generation_summary(
        world=world, manifest=manifest, dataset_dir=dataset_dir
    )
    manifest_checksum_path = write_manifest_checksum(
        manifest_path, dataset_dir=dataset_dir
    )
    dashboard_path = render_dashboard(
        world=world, manifest=manifest, dataset_dir=dataset_dir
    )

    validation_report_path = dataset_dir / "reports" / "validation_report.json"
    validation_report_path.parent.mkdir(parents=True, exist_ok=True)
    validation_report_path.write_text(
        json.dumps(
            {
                "dataset_id": world.metadata.dataset_id,
                "status": "valid" if not all_errors else "invalid",
                "world_errors": list(world_errors),
                "artifact_errors": list(artifact_errors),
            },
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    package_dir = dataset_dir / "package"
    zip_path = (
        package_dir / f"synthetic_dataset_{world.metadata.dataset_id}.zip"
    )
    all_paths = [
        *world_level_files,
        *(document.path for document in documents),
        manifest_path,
        summary_path,
        validation_report_path,
        manifest_checksum_path,
        dashboard_path,
    ]
    create_zip_archive(all_paths, zip_path, arcname_root=dataset_dir)
    package_checksum_path = write_archive_checksum(zip_path)

    return PackageResult(
        manifest_path=manifest_path,
        summary_path=summary_path,
        validation_report_path=validation_report_path,
        dashboard_path=dashboard_path,
        manifest_checksum_path=manifest_checksum_path,
        zip_path=zip_path,
        package_checksum_path=package_checksum_path,
        artifact_errors=artifact_errors,
    )
