from __future__ import annotations

from scripts.synthetic_data.core.content_generator import CountryContent
from scripts.synthetic_data.core.world_models import (
    ScenarioExpectedResult,
    ScenarioStep,
    SyntheticCountry,
    SyntheticScenario,
)


def generate_scenarios(
    *,
    profile: str,
    countries: tuple[SyntheticCountry, ...],
    content_by_country: dict[str, CountryContent],
) -> tuple[SyntheticScenario, ...]:
    """Build the base scenario catalog required by spec section 23 stage 3:
    comparison, source/comment, watchlist+notification, and a data-quality
    scenario targeting whichever generated country has the weakest
    data_confidence (always exists, regardless of seed or profile)."""
    return (
        _comparison_scenario(profile=profile, countries=countries),
        _source_and_comment_scenario(
            profile=profile,
            country=countries[0],
            content=content_by_country[countries[0].slug],
        ),
        _watchlist_change_scenario(
            profile=profile,
            country=countries[0],
            content=content_by_country[countries[0].slug],
        ),
        _data_quality_scenario(profile=profile, countries=countries),
    )


def _comparison_scenario(
    *, profile: str, countries: tuple[SyntheticCountry, ...]
) -> SyntheticScenario:
    country_a, country_b = countries[0], countries[1]
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
    *, profile: str, countries: tuple[SyntheticCountry, ...]
) -> SyntheticScenario:
    weakest = min(
        countries,
        key=lambda country: country.current_metrics["data_confidence"],
    )
    confidence = weakest.current_metrics["data_confidence"]
    return SyntheticScenario(
        scenario_id=f"scenario-data-quality-{weakest.slug}",
        title=f"Review incomplete or conflicting data for {weakest.name}",
        category="data_quality",
        profile=profile,
        initial_state={
            "user_role": "anonymous",
            "country_slug": weakest.slug,
        },
        steps=(
            ScenarioStep(
                action="open_country", target={"country_slug": weakest.slug}
            ),
            ScenarioStep(
                action="open_trust_panel",
                target={"country_slug": weakest.slug},
            ),
        ),
        expected_results=(
            ScenarioExpectedResult(
                description=(
                    f"Trust panel surfaces the low data_confidence "
                    f"({confidence}) for {weakest.name}."
                ),
                check=f"trust_panel_shows_low_confidence:{weakest.slug}",
            ),
        ),
        related_artifacts=(weakest.country_id,),
        risk_labels=("freshness", "data_quality"),
    )
