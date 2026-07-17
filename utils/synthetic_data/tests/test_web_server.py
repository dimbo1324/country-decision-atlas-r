from __future__ import annotations

from fastapi.testclient import TestClient
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
from utils.synthetic_data.web.models import WebGraph
from utils.synthetic_data.web.server import create_app


def _world(seed: int) -> SyntheticWorld:
    return WorldGenerator(input_data=load_world_input()).generate(
        WorldGenerationOptions(seed=seed, profile="balanced", scale="small")
    )


def _client(tmp_path: Path, seed: int) -> tuple[TestClient, WebGraph]:
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
    app = create_app(dataset_dir=dataset_dir, graph=graph)
    return TestClient(app), graph


def test_home_page_serves_as_html(tmp_path: Path) -> None:
    client, graph = _client(tmp_path, seed=31)
    home = graph.sites[0].pages[0]

    response = client.get(f"/sites/{home.path}")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_unknown_page_is_404(tmp_path: Path) -> None:
    client, _ = _client(tmp_path, seed=32)

    response = client.get("/sites/nowhere/at-all.html")

    assert response.status_code == 404


def test_every_anomaly_kind_gets_the_right_http_status(tmp_path: Path) -> None:
    client, graph = _client(tmp_path, seed=33)
    expected_status = {
        "not_found": 404,
        "server_error": 500,
        "redirect": 302,
        "duplicate": 200,
        "empty": 200,
        "huge": 200,
        "broken_encoding": 200,
    }
    seen_kinds: set[str] = set()

    for site in graph.sites:
        for page in site.pages:
            if page.anomaly is None:
                continue
            response = client.get(f"/sites/{page.path}", follow_redirects=False)
            assert response.status_code == expected_status[page.anomaly.kind], (
                page.anomaly.kind
            )
            seen_kinds.add(page.anomaly.kind)

    assert seen_kinds, "no anomalies were generated for this seed"


def test_redirect_points_at_its_declared_target(tmp_path: Path) -> None:
    client, graph = _client(tmp_path, seed=34)

    for site in graph.sites:
        for page in site.pages:
            if page.anomaly is not None and page.anomaly.kind == "redirect":
                response = client.get(
                    f"/sites/{page.path}", follow_redirects=False
                )
                assert (
                    response.headers["location"]
                    == f"/sites/{page.anomaly.redirect_target}"
                )
                return


def test_files_route_rejects_path_traversal(tmp_path: Path) -> None:
    client, _ = _client(tmp_path, seed=35)

    response = client.get("/files/../../../../etc/passwd")

    assert response.status_code == 404


def test_files_route_sets_content_disposition_attachment(
    tmp_path: Path,
) -> None:
    world = _world(seed=36)
    config = load_web_config()
    dataset_dir = tmp_path / world.metadata.dataset_id
    dataset_dir.mkdir()
    documents_dir = dataset_dir / "documents" / "en-US" / "txt"
    documents_dir.mkdir(parents=True)
    fake_doc = documents_dir / "sample.txt"
    fake_doc.write_text("hello", encoding="utf-8")

    graph = build_web_graph(
        world=world, web_config=config, seed=36, dataset_dir=dataset_dir
    )
    app = create_app(dataset_dir=dataset_dir, graph=graph)
    client = TestClient(app)

    response = client.get("/files/documents/en-US/txt/sample.txt")

    assert response.status_code == 200
    assert response.headers["content-disposition"].startswith("attachment")
