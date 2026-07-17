from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, RedirectResponse, Response
from pathlib import Path
from utils.synthetic_data.core.world_models import FICTIONAL_NOTICE
from utils.synthetic_data.web.models import WebGraph


GRAPH_FILENAME = "graph.json"


def load_web_graph(dataset_dir: Path) -> WebGraph:
    graph_path = dataset_dir / "websites" / GRAPH_FILENAME
    if not graph_path.exists():
        raise FileNotFoundError(
            f"{graph_path} not found -- run `generate --formats web` or "
            "`render-web` for this dataset first"
        )
    return WebGraph.model_validate_json(graph_path.read_text(encoding="utf-8"))


def create_app(*, dataset_dir: Path, graph: WebGraph) -> FastAPI:
    """One local server for the whole synthetic web: `/sites/...` serves
    rendered site pages (with real HTTP redirect/500 behavior for the
    matching anomaly kinds), `/files/...` serves already-rendered
    documents as downloads. No nginx, no per-site container, no virtual
    hosts -- one process, path-based routing, per Stage 1's decision."""
    app = FastAPI(
        title="Synthetic Web Environment",
        description=f"{FICTIONAL_NOTICE}. Serves a generated, fictional web "
        "of sites for local testing -- nothing here is a real website.",
    )
    websites_dir = dataset_dir / "websites"

    @app.get("/sites/{page_path:path}")
    def serve_site_page(page_path: str) -> Response:
        page = graph.page_by_path(page_path)
        if page is not None and page.anomaly is not None:
            if page.anomaly.kind == "server_error":
                raise HTTPException(
                    status_code=500,
                    detail=f"Synthetic server error (deliberate test anomaly). {FICTIONAL_NOTICE}.",
                )
            if page.anomaly.kind == "redirect":
                assert page.anomaly.redirect_target is not None
                return RedirectResponse(
                    url=f"/sites/{page.anomaly.redirect_target}",
                    status_code=302,
                )

        file_path = websites_dir / page_path
        if not file_path.is_file():
            raise HTTPException(
                status_code=404,
                detail=f"Not found (synthetic). {FICTIONAL_NOTICE}.",
            )
        media_type = (
            "text/html; charset=utf-8" if file_path.suffix == ".html" else None
        )
        return FileResponse(file_path, media_type=media_type)

    @app.get("/files/{doc_path:path}")
    def serve_file(doc_path: str) -> FileResponse:
        file_path = (dataset_dir / doc_path).resolve()
        if dataset_dir.resolve() not in file_path.parents:
            raise HTTPException(
                status_code=404, detail="Not found (synthetic)."
            )
        if not file_path.is_file():
            raise HTTPException(
                status_code=404,
                detail=f"File not found (synthetic). {FICTIONAL_NOTICE}.",
            )
        return FileResponse(file_path, filename=file_path.name)

    return app
