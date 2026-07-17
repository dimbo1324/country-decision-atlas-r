from __future__ import annotations

from pathlib import Path
from utils.synthetic_data.core.world_generator import (
    WorldGenerationOptions,
    WorldGenerator,
)
from utils.synthetic_data.core.world_input import load_world_input
from utils.synthetic_data.core.world_models import (
    FICTIONAL_NOTICE,
    SyntheticWorld,
)
from utils.synthetic_data.web.anomalies import NO_FILE_ANOMALY_KINDS
from utils.synthetic_data.web.archetypes import load_web_config
from utils.synthetic_data.web.graph import build_web_graph
from utils.synthetic_data.web.html_renderer import (
    RenderedPage,
    render_web_graph,
)
from utils.synthetic_data.web.models import WebGraph


def _world(seed: int) -> SyntheticWorld:
    return WorldGenerator(input_data=load_world_input()).generate(
        WorldGenerationOptions(seed=seed, profile="balanced", scale="small")
    )


def _render(
    tmp_path: Path, seed: int
) -> tuple[WebGraph, list[RenderedPage], Path]:
    world = _world(seed)
    config = load_web_config()
    dataset_dir = tmp_path / world.metadata.dataset_id
    dataset_dir.mkdir()
    graph = build_web_graph(
        world=world, web_config=config, seed=seed, dataset_dir=dataset_dir
    )
    rendered = render_web_graph(
        graph=graph,
        world=world,
        dataset_dir=dataset_dir,
        huge_page_padding_paragraphs=config.huge_page_padding_paragraphs,
    )
    return graph, rendered, dataset_dir


def test_rendered_file_count_excludes_no_file_anomalies(tmp_path: Path) -> None:
    graph, rendered, _ = _render(tmp_path, seed=11)

    expected = [
        page
        for page in graph.all_pages()
        if page.anomaly is None
        or page.anomaly.kind not in NO_FILE_ANOMALY_KINDS
    ]
    assert len(rendered) == len(expected)
    for page in graph.all_pages():
        if (
            page.anomaly is not None
            and page.anomaly.kind in NO_FILE_ANOMALY_KINDS
        ):
            assert page.path not in {r.page_path for r in rendered}


def test_every_rendered_page_carries_the_fictional_notice(
    tmp_path: Path,
) -> None:
    """The "empty" anomaly is the one deliberate exception: its entire
    point is to have essentially no content, so forcing a notice into it
    would defeat the anomaly."""
    graph, rendered, _ = _render(tmp_path, seed=12)
    empty_paths = {
        page.path
        for page in graph.all_pages()
        if page.anomaly is not None and page.anomaly.kind == "empty"
    }

    for page in rendered:
        if page.page_path in empty_paths:
            continue
        text = page.path.read_bytes().decode("utf-8", errors="replace")
        assert FICTIONAL_NOTICE in text, page.page_path


def test_broken_encoding_page_is_not_valid_utf8(tmp_path: Path) -> None:
    _, rendered, _ = _render(tmp_path, seed=13)

    broken = [
        p
        for p in rendered
        if p.page_kind == "anomaly" and "broken-encoding" in p.page_path
    ]
    if not broken:
        return
    raw = broken[0].path.read_bytes()
    decoded_ok = True
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError:
        decoded_ok = False
    assert not decoded_ok


def test_duplicate_page_matches_its_target_bytes(tmp_path: Path) -> None:
    graph, rendered, _ = _render(tmp_path, seed=14)
    by_path = {r.page_path: r for r in rendered}

    for page in graph.all_pages():
        if page.anomaly is not None and page.anomaly.kind == "duplicate":
            assert page.anomaly.duplicate_of is not None
            duplicate_bytes = by_path[page.path].path.read_bytes()
            original_bytes = by_path[
                page.anomaly.duplicate_of
            ].path.read_bytes()
            assert duplicate_bytes == original_bytes


def test_huge_page_is_larger_than_an_ordinary_page(tmp_path: Path) -> None:
    graph, rendered, _ = _render(tmp_path, seed=15)
    by_path = {r.page_path: r for r in rendered}

    home_sizes = [r.size_bytes for r in rendered if r.page_kind == "home"]
    for page in graph.all_pages():
        if page.anomaly is not None and page.anomaly.kind == "huge":
            assert by_path[page.path].size_bytes > max(home_sizes) * 3
