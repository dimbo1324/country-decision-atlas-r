from __future__ import annotations

from pathlib import Path
from utils.synthetic_data.core.world_generator import (
    WorldGenerationOptions,
    WorldGenerator,
)
from utils.synthetic_data.core.world_input import load_world_input
from utils.synthetic_data.core.world_models import SyntheticWorld
from utils.synthetic_data.web.anomalies import ANOMALY_KINDS
from utils.synthetic_data.web.archetypes import WebConfig, load_web_config
from utils.synthetic_data.web.graph import build_web_graph, source_page_urls


def _world(seed: int = 42017, scale: str = "small") -> SyntheticWorld:
    return WorldGenerator(input_data=load_world_input()).generate(
        WorldGenerationOptions(seed=seed, profile="balanced", scale=scale)
    )


def _config() -> WebConfig:
    return load_web_config()


def test_same_seed_produces_the_same_graph(tmp_path: Path) -> None:
    world = _world(seed=101)
    config = _config()

    first = build_web_graph(
        world=world, web_config=config, seed=101, dataset_dir=tmp_path
    )
    second = build_web_graph(
        world=world, web_config=config, seed=101, dataset_dir=tmp_path
    )

    assert first.to_dict() == second.to_dict()


def test_one_site_per_country(tmp_path: Path) -> None:
    world = _world(seed=202)

    graph = build_web_graph(
        world=world, web_config=_config(), seed=202, dataset_dir=tmp_path
    )

    assert len(graph.sites) == len(world.countries)
    assert {site.country_id for site in graph.sites} == {
        country.country_id for country in world.countries
    }


def test_grounded_pages_reference_only_real_world_entities(
    tmp_path: Path,
) -> None:
    world = _world(seed=303)
    source_ids = {
        source.source_id
        for country in world.countries
        for source in country.sources
    }
    article_ids = {article.article_id for article in world.articles}
    signal_ids = {signal.signal_id for signal in world.legal_signals}

    graph = build_web_graph(
        world=world, web_config=_config(), seed=303, dataset_dir=tmp_path
    )

    for page in graph.all_pages():
        if page.kind == "source":
            assert page.related_entity_id in source_ids
        elif page.kind == "article":
            assert page.related_entity_id in article_ids
        elif page.kind == "notice":
            assert page.related_entity_id in signal_ids


def test_home_page_is_always_first_and_about_second(tmp_path: Path) -> None:
    world = _world(seed=404)

    graph = build_web_graph(
        world=world, web_config=_config(), seed=404, dataset_dir=tmp_path
    )

    for site in graph.sites:
        assert site.pages[0].kind == "home"
        assert site.pages[1].kind == "about"


def test_every_anomaly_kind_appears_across_a_seed_range(tmp_path: Path) -> None:
    """Matches the project's own style of probabilistic coverage checks
    (test_world_generator.py's crisis-profile test): with the configured
    default ratios, every anomaly kind should show up somewhere within a
    modest seed range -- if this ever stops being true, the ratios in
    web_config.json drifted too low to be a meaningful test signal."""
    config = _config()
    seen: set[str] = set()

    for seed in range(1, 21):
        world = _world(seed=seed)
        graph = build_web_graph(
            world=world, web_config=config, seed=seed, dataset_dir=tmp_path
        )
        seen.update(
            page.anomaly.kind for page in graph.all_pages() if page.anomaly
        )
        if seen == set(ANOMALY_KINDS):
            break

    assert seen == set(ANOMALY_KINDS)


def test_source_page_urls_covers_every_source_page(tmp_path: Path) -> None:
    world = _world(seed=505)
    graph = build_web_graph(
        world=world, web_config=_config(), seed=505, dataset_dir=tmp_path
    )

    mapping = source_page_urls(graph)
    source_pages = [page for page in graph.all_pages() if page.kind == "source"]

    assert len(mapping) == len(source_pages)
    for page in source_pages:
        assert page.related_entity_id is not None
        assert mapping[page.related_entity_id] == f"/sites/{page.path}"


def test_cross_site_links_never_point_back_at_their_own_site(
    tmp_path: Path,
) -> None:
    world = _world(seed=606)
    graph = build_web_graph(
        world=world, web_config=_config(), seed=606, dataset_dir=tmp_path
    )

    for site in graph.sites:
        home = site.pages[0]
        for link in home.links:
            if link.label.startswith("Related coverage:"):
                assert not link.target_path.startswith(f"{site.slug}/")
