from __future__ import annotations

from utils.synthetic_data.core.content_generator import CountryContent
from utils.synthetic_data.core.world_models import (
    ScenarioExpectedResult,
    ScenarioStep,
    SyntheticCountry,
    SyntheticScenario,
)


_VARIANTS_PER_CATEGORY = 2


def generate_scenarios(
    *,
    profile: str,
    countries: tuple[SyntheticCountry, ...],
    content_by_country: dict[str, CountryContent],
    variants_per_category: int = _VARIANTS_PER_CATEGORY,
) -> tuple[SyntheticScenario, ...]:
    """Build the scenario catalog required by spec section 23 stage 3, with
    up to `variants_per_category` variants per category (comparison,
    source_review, change_notification, data_quality) so manual and
    automated QA has more than one instance to exercise per run. The first
    variant of each category always matches the original single-variant
    behavior (countries[0] as the primary actor, weakest data_confidence
    country first for data_quality), so this stays a pure addition."""
    variant_count = min(variants_per_category, len(countries))
    comparisons = tuple(
        _comparison_scenario(
            profile=profile, country_a=country_a, country_b=country_b
        )
        for country_a, country_b in _distinct_country_pairs(
            countries, variant_count
        )
    )
    source_reviews = tuple(
        _source_and_comment_scenario(
            profile=profile,
            country=country,
            content=content_by_country[country.slug],
        )
        for country in countries[:variant_count]
    )
    change_notifications = tuple(
        _watchlist_change_scenario(
            profile=profile,
            country=country,
            content=content_by_country[country.slug],
        )
        for country in countries[:variant_count]
    )
    data_quality_scenarios = tuple(
        _data_quality_scenario(profile=profile, country=country)
        for country in _weakest_countries(countries, variant_count)
    )
    return (
        comparisons
        + source_reviews
        + change_notifications
        + data_quality_scenarios
    )


def _distinct_country_pairs(
    countries: tuple[SyntheticCountry, ...], variant_count: int
) -> tuple[tuple[SyntheticCountry, SyntheticCountry], ...]:
    pair_count = min(variant_count, len(countries) // 2)
    return tuple(
        (countries[2 * index], countries[2 * index + 1])
        for index in range(pair_count)
    )


def _weakest_countries(
    countries: tuple[SyntheticCountry, ...], variant_count: int
) -> tuple[SyntheticCountry, ...]:
    ordered = sorted(
        countries,
        key=lambda country: country.current_metrics["data_confidence"],
    )
    return tuple(ordered[:variant_count])


def _comparison_scenario(
    *,
    profile: str,
    country_a: SyntheticCountry,
    country_b: SyntheticCountry,
) -> SyntheticScenario:
    return SyntheticScenario(
        scenario_id=f"scenario-compare-{country_a.slug}-{country_b.slug}",
        title=f"Compare {country_a.name} and {country_b.name}",
        category="comparison",
        profile=profile,
        initial_state={"user_role": "anonymous"},
        steps=(
            ScenarioStep(
                action="open_country",
                target={"country_slug": country_a.slug},
            ),
            ScenarioStep(
                action="open_country",
                target={"country_slug": country_b.slug},
            ),
            ScenarioStep(
                action="compare_countries",
                target={
                    "country_slug_a": country_a.slug,
                    "country_slug_b": country_b.slug,
                },
            ),
        ),
        expected_results=(
            ScenarioExpectedResult(
                description=(
                    f"Comparison shows different metric profiles for "
                    f"{country_a.name} and {country_b.name}."
                ),
                check=(
                    f"compare_view_shows_distinct_metrics:"
                    f"{country_a.slug}:{country_b.slug}"
                ),
            ),
        ),
        related_artifacts=(country_a.country_id, country_b.country_id),
        risk_labels=("search",),
    )


def _source_and_comment_scenario(
    *, profile: str, country: SyntheticCountry, content: CountryContent
) -> SyntheticScenario:
    source = country.sources[0]
    comment = content.comments[0]
    return SyntheticScenario(
        scenario_id=f"scenario-source-comment-{country.slug}",
        title=f"Review a source and leave a comment on {country.name}",
        category="source_review",
        profile=profile,
        initial_state={
            "user_role": "authenticated_user",
            "country_slug": country.slug,
        },
        steps=(
            ScenarioStep(
                action="open_country", target={"country_slug": country.slug}
            ),
            ScenarioStep(
                action="open_article",
                target={"article_id": content.article.article_id},
            ),
            ScenarioStep(
                action="open_source", target={"source_id": source.source_id}
            ),
            ScenarioStep(
                action="add_comment",
                target={
                    "article_id": content.article.article_id,
                    "comment_id": comment.comment_id,
                },
            ),
        ),
        expected_results=(
            ScenarioExpectedResult(
                description=(
                    f"Source {source.title} opens and shows its "
                    "confidence level."
                ),
                check=f"source_detail_shows_confidence:{source.source_id}",
            ),
            ScenarioExpectedResult(
                description=(
                    "New comment appears with moderation status "
                    f"{comment.moderation_status}."
                ),
                check=(
                    f"comment_visible_with_status:{comment.comment_id}:"
                    f"{comment.moderation_status}"
                ),
            ),
        ),
        related_artifacts=(
            country.country_id,
            content.article.article_id,
            source.source_id,
            comment.comment_id,
        ),
        risk_labels=("moderation", "authorization"),
    )


def _watchlist_change_scenario(
    *, profile: str, country: SyntheticCountry, content: CountryContent
) -> SyntheticScenario:
    event = country.events[0]
    legal_signal = content.legal_signal
    return SyntheticScenario(
        scenario_id=f"scenario-watchlist-change-{country.slug}",
        title=f"Watch {country.name} and see the {event.metric} change",
        category="change_notification",
        profile=profile,
        initial_state={
            "user_role": "authenticated_user",
            "country_slug": country.slug,
        },
        steps=(
            ScenarioStep(
                action="open_country", target={"country_slug": country.slug}
            ),
            ScenarioStep(
                action="add_to_watchlist",
                target={"country_slug": country.slug},
            ),
            ScenarioStep(
                action="open_what_changed",
                target={"country_slug": country.slug},
            ),
            ScenarioStep(
                action="trigger_notification",
                target={"country_slug": country.slug, "channel": "fake"},
            ),
        ),
        expected_results=(
            ScenarioExpectedResult(
                description=(
                    f"'What changed' shows the {event.metric} "
                    f"{event.direction} event with its legal signal."
                ),
                check=f"what_changed_shows_event:{event.event_id}",
            ),
            ScenarioExpectedResult(
                description=(
                    "A fake-mode notification is queued for the "
                    "watchlisted change."
                ),
                check=(
                    f"fake_notification_queued:{country.slug}:{event.event_id}"
                ),
            ),
        ),
        related_artifacts=(
            country.country_id,
            event.event_id,
            legal_signal.signal_id,
        ),
        risk_labels=("freshness", "notifications"),
    )


def _data_quality_scenario(
    *, profile: str, country: SyntheticCountry
) -> SyntheticScenario:
    confidence = country.current_metrics["data_confidence"]
    return SyntheticScenario(
        scenario_id=f"scenario-data-quality-{country.slug}",
        title=f"Review incomplete or conflicting data for {country.name}",
        category="data_quality",
        profile=profile,
        initial_state={
            "user_role": "anonymous",
            "country_slug": country.slug,
        },
        steps=(
            ScenarioStep(
                action="open_country", target={"country_slug": country.slug}
            ),
            ScenarioStep(
                action="open_trust_panel",
                target={"country_slug": country.slug},
            ),
        ),
        expected_results=(
            ScenarioExpectedResult(
                description=(
                    f"Trust panel surfaces the low data_confidence "
                    f"({confidence}) for {country.name}."
                ),
                check=f"trust_panel_shows_low_confidence:{country.slug}",
            ),
        ),
        related_artifacts=(country.country_id,),
        risk_labels=("freshness", "data_quality"),
    )
