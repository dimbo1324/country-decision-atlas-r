from __future__ import annotations

from utils.synthetic_data.core.seed import SeedFactory
from utils.synthetic_data.web.archetypes import WebConfig
from utils.synthetic_data.web.models import (
    LinkEdge,
    PageAnomaly,
    SitePage,
    SyntheticSite,
)


# not_found/server_error never get real bytes on disk (web/html_renderer.py
# skips them); the other five are real, reachable pages with unusual
# content or behavior. Kept in one place so graph.py, html_renderer.py, and
# server.py can't drift on which kinds exist.
ANOMALY_KINDS = (
    "not_found",
    "server_error",
    "redirect",
    "duplicate",
    "empty",
    "huge",
    "broken_encoding",
)
NO_FILE_ANOMALY_KINDS = frozenset({"not_found", "server_error"})


def _anomaly_page(*, site_slug: str, kind: str, home_path: str) -> SitePage:
    path = f"{site_slug}/anomalies/{kind.replace('_', '-')}.html"
    if kind == "redirect":
        anomaly = PageAnomaly(kind=kind, redirect_target=home_path)
    elif kind == "duplicate":
        anomaly = PageAnomaly(kind=kind, duplicate_of=home_path)
    else:
        anomaly = PageAnomaly(kind=kind)
    return SitePage(
        path=path,
        title=f"({kind.replace('_', ' ')} test page)",
        kind="anomaly",
        anomaly=anomaly,
    )


def assign_anomalies(
    *,
    sites: list[SyntheticSite],
    web_config: WebConfig,
    seed_factory: SeedFactory,
) -> list[SyntheticSite]:
    """For every site and every configured anomaly kind, an independent
    seeded coin flip (probability = web_config.anomaly_ratios[kind])
    decides whether that site gets one instance of that anomaly, linked
    from its home page. Deterministic: same seed -> same set of broken
    pages every time."""
    updated_sites: list[SyntheticSite] = []
    for site in sites:
        home_page = site.pages[0]
        assert home_page.kind == "home", "graph.py must build home page first"

        new_pages: list[SitePage] = []
        new_links: list[LinkEdge] = []
        for kind in ANOMALY_KINDS:
            ratio = web_config.anomaly_ratios[kind]
            rng = seed_factory.rng("web", "anomaly", site.slug, kind)
            if rng.random() >= ratio:
                continue
            anomaly_page = _anomaly_page(
                site_slug=site.slug, kind=kind, home_path=home_page.path
            )
            new_pages.append(anomaly_page)
            new_links.append(
                LinkEdge(
                    target_path=anomaly_page.path,
                    label=anomaly_page.title,
                    kind=(
                        "broken" if kind in NO_FILE_ANOMALY_KINDS else "link"
                    ),
                )
            )

        if not new_pages:
            updated_sites.append(site)
            continue

        updated_home = home_page.model_copy(
            update={"links": home_page.links + tuple(new_links)}
        )
        updated_sites.append(
            site.model_copy(
                update={
                    "pages": (updated_home, *site.pages[1:], *new_pages),
                }
            )
        )
    return updated_sites
