from __future__ import annotations

import html
from dataclasses import dataclass
from pathlib import Path
from utils.synthetic_data.core.world_models import (
    FICTIONAL_NOTICE,
    SyntheticArticle,
    SyntheticComment,
    SyntheticCountry,
    SyntheticLegalSignal,
    SyntheticSource,
    SyntheticWorld,
)
from utils.synthetic_data.web.anomalies import NO_FILE_ANOMALY_KINDS
from utils.synthetic_data.web.assets import (
    FAVICON_DATA_URI,
    PAGE_STYLE,
    placeholder_image_svg,
)
from utils.synthetic_data.web.models import (
    LinkEdge,
    SitePage,
    SyntheticSite,
    WebGraph,
)


@dataclass(frozen=True)
class RenderedPage:
    path: Path
    site_slug: str
    page_path: str
    page_kind: str
    is_anomaly: bool
    size_bytes: int


def _e(value: object) -> str:
    return html.escape(str(value))


def _links_list(links: tuple[LinkEdge, ...]) -> str:
    if not links:
        return ""
    items = "".join(
        f'<li><a class="{"download" if link.kind == "download" else ""}" '
        f'href="/sites/{_e(link.target_path)}">{_e(link.label)}</a></li>'
        if link.kind != "download"
        else f'<li><a class="download" href="{_e(link.target_path)}">'
        f"{_e(link.label)}</a></li>"
        for link in links
    )
    return f'<ul class="links">{items}</ul>'


def _page_shell(*, title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<link rel="icon" href="{FAVICON_DATA_URI}">
<title>{_e(title)}</title>
<style>{PAGE_STYLE}</style>
</head>
<body>
<header>
<h1>{_e(title)}</h1>
<div class="notice">{_e(FICTIONAL_NOTICE)}</div>
</header>
{body}
<footer>{_e(FICTIONAL_NOTICE)} &middot; part of a generated synthetic dataset, not a real website.</footer>
</body>
</html>
"""


def _breadcrumbs(site: SyntheticSite) -> str:
    return (
        f'<nav class="breadcrumbs"><a href="/sites/{site.slug}/index.html">'
        f"{_e(site.title)}</a></nav>"
    )


def _render_home(*, page: SitePage) -> str:
    body = f"{_links_list(page.links)}"
    return _page_shell(title=page.title, body=body)


def _render_about(*, site: SyntheticSite, page: SitePage) -> str:
    body = f"""
{_breadcrumbs(site)}
<p>{_e(site.title)} is a fictional publisher generated for local testing.
It has no real editorial staff, no real readership, and reports on no
real events.</p>
{placeholder_image_svg(label=site.title)}
"""
    return _page_shell(title=page.title, body=body)


def _render_source(
    *,
    site: SyntheticSite,
    page: SitePage,
    source: SyntheticSource,
    country: SyntheticCountry,
) -> str:
    body = f"""
{_breadcrumbs(site)}
<p><strong>Country:</strong> {_e(country.name)}</p>
<p><strong>Confidence:</strong> {source.confidence}/100</p>
<p>{_e(source.title)}</p>
{_links_list(page.links)}
"""
    return _page_shell(title=page.title, body=body)


def _render_article(
    *,
    site: SyntheticSite,
    page: SitePage,
    article: SyntheticArticle,
    comments: tuple[SyntheticComment, ...],
) -> str:
    comments_html = "".join(
        f'<div class="comment"><p>{_e(comment.body)}</p>'
        f'<p class="meta">{_e(comment.moderation_status)} &middot; {_e(comment.created_as_of)}</p></div>'
        for comment in comments
    )
    body = f"""
{_breadcrumbs(site)}
<p class="meta">Published {_e(article.published_as_of)}</p>
<p>{_e(article.summary)}</p>
{_links_list(page.links)}
<h2>Comments</h2>
{comments_html or '<p class="meta">No comments yet.</p>'}
"""
    return _page_shell(title=page.title, body=body)


def _render_notice(
    *, site: SyntheticSite, page: SitePage, signal: SyntheticLegalSignal
) -> str:
    body = f"""
{_breadcrumbs(site)}
<p><strong>Impact:</strong> {_e(signal.impact)}</p>
<p><strong>Effective:</strong> {_e(signal.effective_as_of)}</p>
<p><strong>Confidence:</strong> {signal.confidence}/100</p>
"""
    return _page_shell(title=page.title, body=body)


def _render_redirect_stub(*, target_path: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="0; url=/sites/{_e(target_path)}">
<title>Moved</title>
</head>
<body>
<div class="notice">{_e(FICTIONAL_NOTICE)}</div>
<p>This page moved. If you are not redirected, follow
<a href="/sites/{_e(target_path)}">this link</a>.</p>
</body>
</html>
"""


def _render_empty() -> str:
    return '<!doctype html><html><head><meta charset="utf-8"></head><body></body></html>'


def _render_huge(*, padding_paragraphs: int) -> str:
    filler = "".join(
        f"<p>Synthetic filler paragraph {index}. {FICTIONAL_NOTICE}.</p>"
        for index in range(padding_paragraphs)
    )
    return _page_shell(title="Huge test page", body=filler)


def _render_broken_encoding() -> bytes:
    """Deliberately mis-encoded: the HTML declares utf-8 but the body
    bytes are latin-1, so any UTF-8-honest reader mis-renders the
    non-ASCII text as mojibake -- a real "broken encoding" test fixture,
    not a bug."""
    body = "<p>Bad encoding test: café, naïve, façade, Zürich.</p>"
    page = _page_shell(title="Broken encoding test page", body=body)
    return page.encode("latin-1", errors="replace")


def render_web_graph(
    *,
    graph: WebGraph,
    world: SyntheticWorld,
    dataset_dir: Path,
    huge_page_padding_paragraphs: int,
) -> list[RenderedPage]:
    """Writes every reachable page in `graph` to
    `<dataset_dir>/websites/<site_slug>/...`. Pages whose anomaly kind is
    `not_found`/`server_error` are deliberately skipped -- there is no
    file to write; web/server.py answers those requests from the graph
    itself, not from disk."""
    websites_dir = dataset_dir / "websites"
    countries_by_id = {
        country.country_id: country for country in world.countries
    }
    sources_by_id = {
        source.source_id: source
        for country in world.countries
        for source in country.sources
    }
    articles_by_id = {article.article_id: article for article in world.articles}
    signals_by_id = {signal.signal_id: signal for signal in world.legal_signals}
    comments_by_article: dict[str, list[SyntheticComment]] = {}
    for comment in world.comments:
        comments_by_article.setdefault(comment.article_id, []).append(comment)

    rendered_bytes_by_path: dict[str, bytes] = {}
    rendered: list[RenderedPage] = []

    for site in graph.sites:
        for page in site.pages:
            if (
                page.anomaly is not None
                and page.anomaly.kind in NO_FILE_ANOMALY_KINDS
            ):
                continue

            if page.kind == "home":
                document_text = _render_home(page=page)
            elif page.kind == "about":
                document_text = _render_about(site=site, page=page)
            elif page.kind == "source":
                assert page.related_entity_id is not None
                document_text = _render_source(
                    site=site,
                    page=page,
                    source=sources_by_id[page.related_entity_id],
                    country=countries_by_id[site.country_id],
                )
            elif page.kind == "article":
                assert page.related_entity_id is not None
                article = articles_by_id[page.related_entity_id]
                document_text = _render_article(
                    site=site,
                    page=page,
                    article=article,
                    comments=tuple(
                        comments_by_article.get(article.article_id, [])
                    ),
                )
            elif page.kind == "notice":
                assert page.related_entity_id is not None
                document_text = _render_notice(
                    site=site,
                    page=page,
                    signal=signals_by_id[page.related_entity_id],
                )
            elif page.kind == "anomaly":
                assert page.anomaly is not None
                document_text = None
                if page.anomaly.kind == "redirect":
                    assert page.anomaly.redirect_target is not None
                    document_text = _render_redirect_stub(
                        target_path=page.anomaly.redirect_target
                    )
                elif page.anomaly.kind == "duplicate":
                    assert page.anomaly.duplicate_of is not None
                    document_text = rendered_bytes_by_path[
                        page.anomaly.duplicate_of
                    ].decode("utf-8")
                elif page.anomaly.kind == "empty":
                    document_text = _render_empty()
                elif page.anomaly.kind == "huge":
                    document_text = _render_huge(
                        padding_paragraphs=huge_page_padding_paragraphs
                    )
            else:
                raise ValueError(f"unknown page kind: {page.kind!r}")

            output_path = websites_dir / page.path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            if (
                page.kind == "anomaly"
                and page.anomaly is not None
                and page.anomaly.kind == "broken_encoding"
            ):
                payload = _render_broken_encoding()
            else:
                assert document_text is not None
                payload = document_text.encode("utf-8")
            output_path.write_bytes(payload)
            rendered_bytes_by_path[page.path] = payload

            rendered.append(
                RenderedPage(
                    path=output_path,
                    site_slug=site.slug,
                    page_path=page.path,
                    page_kind=page.kind,
                    is_anomaly=page.anomaly is not None,
                    size_bytes=len(payload),
                )
            )

    return rendered
