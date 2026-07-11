from __future__ import annotations

from pathlib import Path
from scripts.synthetic_data.core.dashboard import render_dashboard
from scripts.synthetic_data.core.dataset_packager import (
    package_dataset,
    render_dataset_documents,
)
from scripts.synthetic_data.core.locale_corpus import load_locale_corpus
from scripts.synthetic_data.core.manifest import build_manifest
from scripts.synthetic_data.core.world_generator import (
    WorldGenerationOptions,
    WorldGenerator,
)
from scripts.synthetic_data.core.world_input import load_world_input
from scripts.synthetic_data.core.world_models import (
    FICTIONAL_NOTICE,
    SyntheticWorld,
)
from scripts.synthetic_data.core.world_validation import validate_world


def _world() -> SyntheticWorld:
    return WorldGenerator(input_data=load_world_input()).generate(
        WorldGenerationOptions(seed=42017, profile="balanced")
    )


def test_dashboard_lists_every_country_and_scenario(tmp_path: Path) -> None:
    world = _world()
    corpus = load_locale_corpus()
    documents = render_dataset_documents(
        world=world,
        locale_corpus=corpus,
        dataset_dir=tmp_path,
        formats=("json",),
    )
    manifest = build_manifest(
        world=world,
        dataset_dir=tmp_path,
        documents=documents,
        world_level_files=[],
    )

    path = render_dashboard(
        world=world, manifest=manifest, dataset_dir=tmp_path
    )
    html = path.read_text(encoding="utf-8")

    assert path == tmp_path / "reports" / "dashboard.html"
    assert FICTIONAL_NOTICE in html
    for country in world.countries:
        assert country.name in html
        assert country.code in html
    for scenario in world.scenarios:
        assert scenario.title in html


def test_dashboard_excludes_locale_less_world_level_files_from_artifact_table(
    tmp_path: Path,
) -> None:
    world = _world()
    corpus = load_locale_corpus()
    documents = render_dataset_documents(
        world=world,
        locale_corpus=corpus,
        dataset_dir=tmp_path,
        formats=("json",),
    )
    canonical_dir = tmp_path / "canonical"
    canonical_dir.mkdir(parents=True, exist_ok=True)
    world_level_file = canonical_dir / "synthetic_world.json"
    world_level_file.write_text("{}", encoding="utf-8")
    manifest = build_manifest(
        world=world,
        dataset_dir=tmp_path,
        documents=documents,
        world_level_files=[world_level_file],
    )

    path = render_dashboard(
        world=world, manifest=manifest, dataset_dir=tmp_path
    )
    html = path.read_text(encoding="utf-8")

    assert "<td>-</td>" not in html


def test_dashboard_links_resolve_to_real_files_on_disk(tmp_path: Path) -> None:
    world = _world()
    corpus = load_locale_corpus()
    _canonical_json(world, tmp_path)
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

    html = result.dashboard_path.read_text(encoding="utf-8")
    reports_dir = result.dashboard_path.parent
    for line in html.splitlines():
        if 'href="../documents/' not in line:
            continue
        start = line.index('href="../documents/') + len('href="')
        end = line.index('"', start)
        relative_href = line[start:end]
        assert (reports_dir / relative_href).resolve().exists()


def _canonical_json(world: SyntheticWorld, dataset_dir: Path) -> None:
    import json

    canonical_dir = dataset_dir / "canonical"
    canonical_dir.mkdir(parents=True, exist_ok=True)
    (canonical_dir / "synthetic_world.json").write_text(
        json.dumps(world.to_dict(), ensure_ascii=False), encoding="utf-8"
    )
