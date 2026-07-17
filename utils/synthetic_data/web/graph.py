from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from utils.synthetic_data.core.document_rendering.context import (
    GeneratedDocument,
)
from utils.synthetic_data.core.seed import SeedFactory
from utils.synthetic_data.core.world_models import (
    SyntheticCountry,
    SyntheticWorld,
)
from utils.synthetic_data.web.anomalies import assign_anomalies
from utils.synthetic_data.web.archetypes import SiteArchetype, WebConfig
from utils.synthetic_data.web.models import (
    LinkEdge,
    SitePage,
    SyntheticSite,
    WebGraph,
)


def _site_slug(country: SyntheticCountry, archetype_slug: str) -> str:
    return f"{country.slug}-{archetype_slug}".replace("_", "-")


def _grounded_pages(
    *,
    country: SyntheticCountry,
    world: SyntheticWorld,
    archetype: SiteArchetype,
    site_slug: str,
    documents_by_country: dict[str, list[GeneratedDocument]],
    dataset_dir: Path,
) -> list[SitePage]:
    """Build every page this site can honestly host for its country:
    one page per source/article/legal-signal the country actually has,
    filtered to the kinds the archetype claims to publish. Never invents
    an entity the world doesn't already contain."""
    pages: list[SitePage] = []
    country_documents = documents_by_country.get(country.country_id, [])
    # Server-root-absolute (not page-relative) so the href is correct
    # regardless of how deep the linking page sits -- web/server.py mounts
    # /files/ as a top-level route over dataset_dir.
    download_links = tuple(
        LinkEdge(
            target_path=(
                f"/files/{document.path.relative_to(dataset_dir).as_posix()}"
            ),
            label=f"Download ({document.file_format}, {document.locale})",
            kind="download",
        )
        for document in sorted(
            country_documents, key=lambda d: d.path.as_posix()
        )[:3]
    )

    if "source" in archetype.page_kinds:
        for source in country.sources:
            pages.append(
                SitePage(
                    path=f"{site_slug}/sources/{source.source_id}.html",
                    title=source.title,
                    kind="source",
                    country_id=country.country_id,
                    related_entity_id=source.source_id,
                    links=download_links,
                )
            )

    if "article" in archetype.page_kinds:
        for article in world.articles:
            if article.country_id != country.country_id:
                continue
            pages.append(
                SitePage(
                    path=f"{site_slug}/articles/{article.article_id}.html",
                    title=article.title,
                    kind="article",
                    country_id=country.country_id,
                    related_entity_id=article.article_id,
                    links=download_links,
                )
            )

    if "notice" in archetype.page_kinds:
        for signal in world.legal_signals:
            if signal.country_id != country.country_id:
                continue
            pages.append(
                SitePage(
                    path=f"{site_slug}/notices/{signal.signal_id}.html",
                    title=f"Notice: {signal.impact} impact effective {signal.effective_as_of}",
                    kind="notice",
                    country_id=country.country_id,
                    related_entity_id=signal.signal_id,
                )
            )

    return pages


def _cross_site_links(
    *,
    site_slug: str,
    all_site_slugs: Sequence[str],
    config: WebConfig,
    seed_factory: SeedFactory,
) -> list[LinkEdge]:
    others = [slug for slug in all_site_slugs if slug != site_slug]
    if not others:
        return []
    rng = seed_factory.rng("web", "cross_site_links", site_slug)
    count = min(
        len(others),
        rng.randint(config.cross_site_links_min, config.cross_site_links_max),
    )
    chosen = rng.sample(others, count)
    return [
        LinkEdge(
            target_path=f"{target}/index.html",
            label=f"Related coverage: {target}",
            kind="link",
        )
        for target in sorted(chosen)
    ]


def build_web_graph(
    *,
    world: SyntheticWorld,
    web_config: WebConfig,
    seed: int,
    dataset_dir: Path,
    documents: Sequence[GeneratedDocument] = (),
) -> WebGraph:
    """Deterministically builds the whole synthetic web for one dataset:
    one site per country (archetype chosen from the seed), grounded pages
    for every source/article/legal-signal the archetype is willing to
    publish, a home+about page per site, cross-site links between homes,
    and deliberately broken anomaly pages/links (web/anomalies.py)."""
    seed_factory = SeedFactory(seed)
    archetype_slugs = [
        archetype.slug for archetype in web_config.site_archetypes
    ]
    documents_by_country: dict[str, list[GeneratedDocument]] = {}
    for document in documents:
        documents_by_country.setdefault(document.country_id, []).append(
            document
        )

    site_plan: list[
        tuple[SyntheticCountry, SiteArchetype, str, list[SitePage]]
    ] = []
    for country in world.countries:
        rng = seed_factory.rng("web", "site_archetype", country.slug)
        archetype = web_config.archetype_by_slug(rng.choice(archetype_slugs))
        site_slug = _site_slug(country, archetype.slug)
        grounded = _grounded_pages(
            country=country,
            world=world,
            archetype=archetype,
            site_slug=site_slug,
            documents_by_country=documents_by_country,
            dataset_dir=dataset_dir,
        )
        site_plan.append((country, archetype, site_slug, grounded))

    all_site_slugs = [site_slug for _, _, site_slug, _ in site_plan]

    sites: list[SyntheticSite] = []
    for country, archetype, site_slug, grounded_pages in site_plan:
        about_page = SitePage(
            path=f"{site_slug}/about.html",
            title=f"About {archetype.title_for(country.name)}",
            kind="about",
            country_id=country.country_id,
        )
        home_links = [
            LinkEdge(target_path=about_page.path, label="About", kind="link"),
            *(
                LinkEdge(target_path=page.path, label=page.title, kind="link")
                for page in grounded_pages
            ),
            *_cross_site_links(
                site_slug=site_slug,
                all_site_slugs=all_site_slugs,
                config=web_config,
                seed_factory=seed_factory,
            ),
        ]
        home_page = SitePage(
            path=f"{site_slug}/index.html",
            title=archetype.title_for(country.name),
            kind="home",
            country_id=country.country_id,
            links=tuple(home_links),
        )
        sites.append(
            SyntheticSite(
                slug=site_slug,
                title=archetype.title_for(country.name),
                archetype=archetype.slug,
                country_id=country.country_id,
                pages=(home_page, about_page, *grounded_pages),
            )
        )

    sites = assign_anomalies(
        sites=sites, web_config=web_config, seed_factory=seed_factory
    )
    return WebGraph(
        dataset_id=world.metadata.dataset_id, seed=seed, sites=tuple(sites)
    )


def source_page_urls(graph: WebGraph) -> dict[str, str]:
    """Maps every source_id that got a dedicated page to the server path
    that renders it (`/sites/<path>`). Kept separate from
    `SyntheticSource.url` on purpose -- that field is validated
    (core/world_validation.py) to always start with `synthetic://` and
    must never change; this mapping is how anything that wants "the real
    page for this source" resolves it instead."""
    return {
        page.related_entity_id: f"/sites/{page.path}"
        for site in graph.sites
        for page in site.pages
        if page.kind == "source" and page.related_entity_id is not None
    }
