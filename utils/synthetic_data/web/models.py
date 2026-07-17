from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class _FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True)


class LinkEdge(_FrozenModel):
    """One hyperlink rendered on a page. `target_path` is a site-tree-
    relative path (e.g. `gov-portal/sources/source-x.html`) resolved
    against the whole website root, never an absolute URL -- the server
    decides the host/port, not the graph."""

    target_path: str
    label: str
    kind: str = "link"  # "link" | "download"


class PageAnomaly(_FrozenModel):
    """Marks a page as deliberately broken. `kind` drives both how
    html_renderer.py renders the page body and how server.py answers a
    request for it -- see web/server.py's ANOMALY_STATUS table."""

    kind: str  # not_found | server_error | redirect | duplicate | empty | huge | broken_encoding
    redirect_target: str | None = None
    duplicate_of: str | None = None


class SitePage(_FrozenModel):
    path: str
    title: str
    kind: str  # home | about | source | article | notice | anomaly
    country_id: str | None = None
    related_entity_id: str | None = None
    links: tuple[LinkEdge, ...] = ()
    anomaly: PageAnomaly | None = None


class SyntheticSite(_FrozenModel):
    slug: str
    title: str
    archetype: str
    country_id: str
    pages: tuple[SitePage, ...]

    def page(self, path: str) -> SitePage | None:
        for page in self.pages:
            if page.path == path:
                return page
        return None


class WebGraph(_FrozenModel):
    dataset_id: str
    seed: int
    sites: tuple[SyntheticSite, ...]

    def page_by_path(self, path: str) -> SitePage | None:
        for site in self.sites:
            page = site.page(path)
            if page is not None:
                return page
        return None

    def all_pages(self) -> tuple[SitePage, ...]:
        return tuple(page for site in self.sites for page in site.pages)

    def to_dict(self) -> dict[str, object]:
        return self.model_dump(mode="json")
