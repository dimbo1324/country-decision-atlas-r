from __future__ import annotations

from collections.abc import Collection
from pathlib import Path
from utils.synthetic_data.web.anomalies import ANOMALY_KINDS
from utils.synthetic_data.web.models import WebGraph


def validate_web_graph(
    graph: WebGraph,
    *,
    dataset_dir: Path,
    downloadable_paths: Collection[str] = (),
) -> tuple[str, ...]:
    """Structural checks over an already-built graph (spec-equivalent of
    core/world_validation.py, scoped to the web layer):

    - every ordinary link resolves to a real page in the graph;
    - every link marked "broken" (the not_found/server_error anomaly
      links) does NOT resolve -- confirms the anomaly is genuinely
      broken, not accidentally valid;
    - every download link points at a document that was actually
      rendered;
    - every non-`not_found`/`server_error` page has a file on disk.
    """
    errors: list[str] = []
    all_page_paths = {page.path for page in graph.all_pages()}
    # not_found/server_error pages exist in the graph (so anomaly links can
    # reference them) but never get a rendered file -- "broken" links must
    # resolve to one of *those*, not to a page that actually serves fine.
    servable_page_paths = {
        page.path
        for page in graph.all_pages()
        if page.anomaly is None
        or page.anomaly.kind not in ("not_found", "server_error")
    }
    downloadable = set(downloadable_paths)

    for site in graph.sites:
        for page in site.pages:
            for link in page.links:
                if link.kind == "download":
                    doc_path = link.target_path.removeprefix("/files/")
                    if doc_path not in downloadable:
                        errors.append(
                            f"{page.path}: download link {link.target_path!r} "
                            "does not match any rendered document"
                        )
                    continue
                if link.kind == "broken":
                    if link.target_path in servable_page_paths:
                        errors.append(
                            f"{page.path}: link {link.target_path!r} is marked "
                            "broken but resolves to a real page"
                        )
                    continue
                if link.target_path not in all_page_paths:
                    errors.append(
                        f"{page.path}: link {link.target_path!r} does not "
                        "resolve to any page in the graph"
                    )

            if (
                page.anomaly is not None
                and page.anomaly.kind not in ANOMALY_KINDS
            ):
                errors.append(
                    f"{page.path}: unknown anomaly kind {page.anomaly.kind!r}"
                )
            if (
                page.anomaly is not None
                and page.anomaly.kind == "redirect"
                and page.anomaly.redirect_target not in all_page_paths
            ):
                errors.append(
                    f"{page.path}: redirect target "
                    f"{page.anomaly.redirect_target!r} does not resolve"
                )
            if (
                page.anomaly is not None
                and page.anomaly.kind == "duplicate"
                and page.anomaly.duplicate_of not in all_page_paths
            ):
                errors.append(
                    f"{page.path}: duplicate_of "
                    f"{page.anomaly.duplicate_of!r} does not resolve"
                )

            anomaly_kind = (
                page.anomaly.kind if page.anomaly is not None else None
            )
            no_file_expected = anomaly_kind in ("not_found", "server_error")
            file_path = dataset_dir / "websites" / page.path
            if no_file_expected and file_path.exists():
                errors.append(
                    f"{page.path}: a {anomaly_kind} anomaly page "
                    "unexpectedly has a file on disk"
                )
            if not no_file_expected and not file_path.exists():
                errors.append(
                    f"{page.path}: expected a rendered file, found none"
                )

    return tuple(errors)
