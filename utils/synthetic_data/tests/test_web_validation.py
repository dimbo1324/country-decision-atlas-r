from __future__ import annotations

from pathlib import Path
from utils.synthetic_data.core.world_generator import (
    WorldGenerationOptions,
    WorldGenerator,
)
from utils.synthetic_data.core.world_input import load_world_input
from utils.synthetic_data.core.world_models import SyntheticWorld
from utils.synthetic_data.web.archetypes import load_web_config
from utils.synthetic_data.web.graph import build_web_graph
from utils.synthetic_data.web.html_renderer import render_web_graph
from utils.synthetic_data.web.models import LinkEdge, WebGraph
from utils.synthetic_data.web.validation import validate_web_graph


def _world(seed: int) -> SyntheticWorld:
    return WorldGenerator(input_data=load_world_input()).generate(
        WorldGenerationOptions(seed=seed, profile="balanced", scale="small")
    )


def _built_and_rendered(tmp_path: Path, seed: int) -> tuple[WebGraph, Path]:
    world = _world(seed)
    config = load_web_config()
    dataset_dir = tmp_path / world.metadata.dataset_id
    dataset_dir.mkdir()
    graph = build_web_graph(
        world=world, web_config=config, seed=seed, dataset_dir=dataset_dir
    )
    render_web_graph(
        graph=graph,
        world=world,
        dataset_dir=dataset_dir,
        huge_page_padding_paragraphs=config.huge_page_padding_paragraphs,
    )
    return graph, dataset_dir


def test_a_freshly_rendered_graph_has_no_validation_errors(
    tmp_path: Path,
) -> None:
    for seed in (1, 2, 3, 4, 5):
        graph, dataset_dir = _built_and_rendered(tmp_path, seed)
        errors = validate_web_graph(graph, dataset_dir=dataset_dir)
        assert errors == (), f"seed {seed}: {errors}"


def test_a_dangling_link_is_caught(tmp_path: Path) -> None:
    graph, dataset_dir = _built_and_rendered(tmp_path, seed=21)
    site = graph.sites[0]
    home = site.pages[0]
    bad_home = home.model_copy(
        update={
            "links": (
                *home.links,
                LinkEdge(target_path="nowhere/at-all.html", label="bad"),
            )
        }
    )
    bad_site = site.model_copy(update={"pages": (bad_home, *site.pages[1:])})
    bad_graph = graph.model_copy(update={"sites": (bad_site, *graph.sites[1:])})

    errors = validate_web_graph(bad_graph, dataset_dir=dataset_dir)

    assert any("does not resolve" in error for error in errors)


def test_a_broken_link_that_actually_resolves_is_caught(tmp_path: Path) -> None:
    """A link marked kind="broken" (i.e. claiming to be an intentional
    404/500) must NOT point at a page that actually serves fine -- that
    would mean the anomaly silently isn't broken anymore."""
    graph, dataset_dir = _built_and_rendered(tmp_path, seed=22)
    site = graph.sites[0]
    home = site.pages[0]
    bad_home = home.model_copy(
        update={
            "links": (
                *home.links,
                LinkEdge(
                    target_path=home.path, label="fake broken", kind="broken"
                ),
            )
        }
    )
    bad_site = site.model_copy(update={"pages": (bad_home, *site.pages[1:])})
    bad_graph = graph.model_copy(update={"sites": (bad_site, *graph.sites[1:])})

    errors = validate_web_graph(bad_graph, dataset_dir=dataset_dir)

    assert any("resolves to a real page" in error for error in errors)


def test_missing_rendered_file_is_caught(tmp_path: Path) -> None:
    graph, dataset_dir = _built_and_rendered(tmp_path, seed=23)
    site = graph.sites[0]
    about_path = dataset_dir / "websites" / site.pages[1].path
    about_path.unlink()

    errors = validate_web_graph(graph, dataset_dir=dataset_dir)

    assert any("expected a rendered file" in error for error in errors)


def test_download_link_without_a_matching_document_is_caught(
    tmp_path: Path,
) -> None:
    graph, dataset_dir = _built_and_rendered(tmp_path, seed=24)
    site = graph.sites[0]
    home = site.pages[0]
    bad_home = home.model_copy(
        update={
            "links": (
                *home.links,
                LinkEdge(
                    target_path="/files/documents/en-US/pdf/copyable/ghost.pdf",
                    label="ghost download",
                    kind="download",
                ),
            )
        }
    )
    bad_site = site.model_copy(update={"pages": (bad_home, *site.pages[1:])})
    bad_graph = graph.model_copy(update={"sites": (bad_site, *graph.sites[1:])})

    errors = validate_web_graph(bad_graph, dataset_dir=dataset_dir)

    assert any(
        "does not match any rendered document" in error for error in errors
    )
