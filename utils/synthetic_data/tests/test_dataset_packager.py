from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path
from utils.synthetic_data.core.dataset_packager import (
    package_dataset,
    render_dataset_documents,
)
from utils.synthetic_data.core.locale_corpus import load_locale_corpus
from utils.synthetic_data.core.world_generator import (
    WorldGenerationOptions,
    WorldGenerator,
)
from utils.synthetic_data.core.world_input import load_world_input
from utils.synthetic_data.core.world_models import SyntheticWorld
from utils.synthetic_data.core.world_validation import validate_world


def _world() -> SyntheticWorld:
    return WorldGenerator(input_data=load_world_input()).generate(
        WorldGenerationOptions(seed=42017, profile="balanced")
    )


def _write_canonical_json(world: SyntheticWorld, dataset_dir: Path) -> None:
    canonical_dir = dataset_dir / "canonical"
    canonical_dir.mkdir(parents=True, exist_ok=True)
    (canonical_dir / "synthetic_world.json").write_text(
        json.dumps(world.to_dict(), ensure_ascii=False), encoding="utf-8"
    )


def test_render_dataset_documents_covers_every_recipe_and_requested_format(
    tmp_path: Path,
) -> None:
    world = _world()
    corpus = load_locale_corpus()

    documents = render_dataset_documents(
        world=world,
        locale_corpus=corpus,
        dataset_dir=tmp_path,
        formats=("json", "txt"),
    )

    assert len(documents) == len(world.document_recipes) * 2
    assert {doc.file_format for doc in documents} == {"json", "txt"}
    assert {doc.locale for doc in documents} == {
        recipe.locale for recipe in world.document_recipes
    }


def test_package_dataset_writes_manifest_report_summary_and_zip(
    tmp_path: Path,
) -> None:
    world = _world()
    corpus = load_locale_corpus()
    _write_canonical_json(world, tmp_path)
    documents = render_dataset_documents(
        world=world,
        locale_corpus=corpus,
        dataset_dir=tmp_path,
        formats=("json", "txt"),
    )
    world_errors = validate_world(world)

    result = package_dataset(
        world=world,
        world_errors=world_errors,
        dataset_dir=tmp_path,
        documents=documents,
    )

    assert result.artifact_errors == ()
    assert result.manifest_path.exists()
    assert result.summary_path.exists()
    assert result.validation_report_path.exists()
    assert result.dashboard_path.exists()
    assert result.manifest_checksum_path.exists()
    assert result.zip_path.exists()
    assert result.package_checksum_path.exists()

    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["dataset_id"] == world.metadata.dataset_id
    assert manifest["artifact_count"] == len(manifest["artifacts"])
    assert manifest["artifact_count"] >= len(documents)

    report = json.loads(
        result.validation_report_path.read_text(encoding="utf-8")
    )
    assert report["status"] == "valid"
    assert report["world_errors"] == []
    assert report["artifact_errors"] == []


def test_manifest_entries_have_correct_checksums(tmp_path: Path) -> None:
    world = _world()
    corpus = load_locale_corpus()
    _write_canonical_json(world, tmp_path)
    documents = render_dataset_documents(
        world=world,
        locale_corpus=corpus,
        dataset_dir=tmp_path,
        formats=("json",),
    )
    world_errors = validate_world(world)

    result = package_dataset(
        world=world,
        world_errors=world_errors,
        dataset_dir=tmp_path,
        documents=documents,
    )
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))

    for entry in manifest["artifacts"]:
        artifact_path = tmp_path / entry["path"]
        assert artifact_path.exists()
        digest = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
        assert entry["sha256"] == digest
        assert entry["size_bytes"] == artifact_path.stat().st_size


def test_manifest_and_package_checksums_are_correct(tmp_path: Path) -> None:
    world = _world()
    corpus = load_locale_corpus()
    _write_canonical_json(world, tmp_path)
    documents = render_dataset_documents(
        world=world,
        locale_corpus=corpus,
        dataset_dir=tmp_path,
        formats=("json",),
    )
    world_errors = validate_world(world)

    result = package_dataset(
        world=world,
        world_errors=world_errors,
        dataset_dir=tmp_path,
        documents=documents,
    )

    manifest_digest = hashlib.sha256(
        result.manifest_path.read_bytes()
    ).hexdigest()
    manifest_checksum_line = result.manifest_checksum_path.read_text(
        encoding="utf-8"
    ).strip()
    assert manifest_checksum_line == f"{manifest_digest}  manifest.json"

    zip_digest = hashlib.sha256(result.zip_path.read_bytes()).hexdigest()
    package_checksum_line = result.package_checksum_path.read_text(
        encoding="utf-8"
    ).strip()
    assert package_checksum_line == f"{zip_digest}  {result.zip_path.name}"

    with zipfile.ZipFile(result.zip_path) as archive:
        assert "reports/manifest.sha256" in archive.namelist()
        assert "reports/dashboard.html" in archive.namelist()


def test_zip_package_contains_manifest_and_every_document(
    tmp_path: Path,
) -> None:
    world = _world()
    corpus = load_locale_corpus()
    _write_canonical_json(world, tmp_path)
    documents = render_dataset_documents(
        world=world,
        locale_corpus=corpus,
        dataset_dir=tmp_path,
        formats=("json",),
    )
    world_errors = validate_world(world)

    result = package_dataset(
        world=world,
        world_errors=world_errors,
        dataset_dir=tmp_path,
        documents=documents,
    )

    with zipfile.ZipFile(result.zip_path) as archive:
        names = set(archive.namelist())

    assert "manifest.json" in names
    assert "canonical/synthetic_world.json" in names
    assert "reports/validation_report.json" in names
    for document in documents:
        assert document.path.relative_to(tmp_path).as_posix() in names


def test_package_dataset_reports_artifact_errors_without_raising(
    tmp_path: Path,
) -> None:
    world = _world()
    corpus = load_locale_corpus()
    _write_canonical_json(world, tmp_path)
    documents = render_dataset_documents(
        world=world,
        locale_corpus=corpus,
        dataset_dir=tmp_path,
        formats=("json",),
    )
    # Corrupt one rendered artifact so the structural check catches it.
    documents[0].path.write_text("not json", encoding="utf-8")
    world_errors = validate_world(world)

    result = package_dataset(
        world=world,
        world_errors=world_errors,
        dataset_dir=tmp_path,
        documents=documents,
    )

    assert result.artifact_errors
    report = json.loads(
        result.validation_report_path.read_text(encoding="utf-8")
    )
    assert report["status"] == "invalid"
