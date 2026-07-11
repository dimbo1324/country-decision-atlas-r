from __future__ import annotations

from collections.abc import Collection
from scripts.synthetic_data.core.locale_corpus import REQUIRED_LOCALES
from scripts.synthetic_data.core.world_input import REQUIRED_METRICS
from scripts.synthetic_data.core.world_models import SyntheticWorld


class WorldValidationError(RuntimeError):
    pass


_ALLOWED_MODERATION_STATUSES = frozenset({"approved", "pending", "hidden"})
_ALLOWED_LEGAL_IMPACTS = frozenset({"positive", "negative", "neutral"})
_EMAIL_DOMAIN_SUFFIX = "@example.test"


def validate_world(
    world: SyntheticWorld,
    *,
    forbidden_country_names: Collection[str] = (),
    expected_locales: Collection[str] = REQUIRED_LOCALES,
) -> tuple[str, ...]:
    errors: list[str] = []
    country_ids: set[str] = set()
    country_codes: set[str] = set()
    country_slugs: set[str] = set()
    country_names: set[str] = set()
    event_ids_by_country: dict[str, set[str]] = {}
    source_ids_by_country: dict[str, set[str]] = {}
    forbidden_names = {name.casefold() for name in forbidden_country_names}

    if not 4 <= len(world.countries) <= 5:
        errors.append("world must contain between 4 and 5 countries")

    for country in world.countries:
        for identity, seen, label in (
            (country.country_id, country_ids, "country id"),
            (country.code, country_codes, "country code"),
            (country.slug, country_slugs, "country slug"),
            (country.name.casefold(), country_names, "country name"),
        ):
            if identity in seen:
                errors.append(f"duplicate {label}: {identity}")
            seen.add(identity)
        if not country.code.startswith("SYN-"):
            errors.append(f"{country.slug}: code must use the SYN- prefix")
        if country.name.casefold() in forbidden_names:
            errors.append(f"{country.slug}: country name is forbidden")
        if len(country.metric_history) != 3:
            errors.append(
                f"{country.slug}: metric history must contain 3 snapshots"
            )
            continue

        previous_date = ""
        changed_metrics: set[str] = set()
        for previous_snapshot, snapshot in zip(
            (None, *country.metric_history),
            country.metric_history,
            strict=False,
        ):
            if snapshot.as_of <= previous_date:
                errors.append(
                    f"{country.slug}: metric snapshots must be chronological"
                )
            previous_date = snapshot.as_of
            if set(snapshot.metrics) != set(REQUIRED_METRICS):
                errors.append(f"{country.slug}: metric set is incomplete")
            for metric, value in snapshot.metrics.items():
                if not 0 <= value <= 100:
                    errors.append(f"{country.slug}: {metric} is outside 0..100")
                if (
                    previous_snapshot is not None
                    and previous_snapshot.metrics.get(metric) != value
                ):
                    changed_metrics.add(metric)

        explained_metrics = {event.metric for event in country.events}
        unexplained_metrics = changed_metrics - explained_metrics
        if unexplained_metrics:
            errors.append(
                f"{country.slug}: unexplained metric change without a "
                f"matching event: {sorted(unexplained_metrics)}"
            )

        current = country.current_metrics
        if all(value >= 70 for value in current.values()):
            errors.append(
                f"{country.slug}: country cannot be positive in every metric"
            )
        if not country.strengths:
            errors.append(f"{country.slug}: at least one strength is required")
        if not country.risks:
            errors.append(f"{country.slug}: at least one risk is required")

        event_ids = {event.event_id for event in country.events}
        if not event_ids:
            errors.append(f"{country.slug}: at least one event is required")
        for event in country.events:
            if event.country_id != country.country_id:
                errors.append(f"{country.slug}: event has another country id")
            if event.metric not in REQUIRED_METRICS:
                errors.append(
                    f"{country.slug}: event references an unknown metric"
                )
            if event.direction not in {"improved", "declined"}:
                errors.append(f"{country.slug}: event direction is invalid")
        source_ids: set[str] = set()
        for source in country.sources:
            source_ids.add(source.source_id)
            if source.country_id != country.country_id:
                errors.append(f"{country.slug}: source has another country id")
            if source.event_id not in event_ids:
                errors.append(
                    f"{country.slug}: source must reference a country event"
                )
            if not source.url.startswith("synthetic://"):
                errors.append(
                    f"{country.slug}: source URL must remain synthetic"
                )
            if not 0 <= source.confidence <= 100:
                errors.append(
                    f"{country.slug}: source confidence is outside 0..100"
                )
        event_ids_by_country[country.country_id] = event_ids
        source_ids_by_country[country.country_id] = source_ids

    _validate_content(
        world,
        errors,
        country_ids=country_ids,
        event_ids_by_country=event_ids_by_country,
        source_ids_by_country=source_ids_by_country,
        expected_locales=expected_locales,
    )
    return tuple(errors)


def _validate_content(
    world: SyntheticWorld,
    errors: list[str],
    *,
    country_ids: set[str],
    event_ids_by_country: dict[str, set[str]],
    source_ids_by_country: dict[str, set[str]],
    expected_locales: Collection[str],
) -> None:
    user_ids: set[str] = set()
    for user in world.users:
        if user.user_id in user_ids:
            errors.append(f"duplicate user id: {user.user_id}")
        user_ids.add(user.user_id)
        if not user.email.endswith(_EMAIL_DOMAIN_SUFFIX):
            errors.append(
                f"{user.user_id}: email must use the {_EMAIL_DOMAIN_SUFFIX} "
                "reserved domain"
            )

    author_ids: set[str] = set()
    for author in world.authors:
        if author.author_id in author_ids:
            errors.append(f"duplicate author id: {author.author_id}")
        author_ids.add(author.author_id)
        if author.user_id not in user_ids:
            errors.append(
                f"{author.author_id}: author must reference an existing user"
            )

    article_ids: set[str] = set()
    for article in world.articles:
        if article.article_id in article_ids:
            errors.append(f"duplicate article id: {article.article_id}")
        article_ids.add(article.article_id)
        if article.author_id not in author_ids:
            errors.append(
                f"{article.article_id}: article must reference an "
                "existing author"
            )
        if article.country_id not in country_ids:
            errors.append(
                f"{article.article_id}: article must reference an "
                "existing country"
            )
        allowed_sources = source_ids_by_country.get(article.country_id, set())
        for source_id in article.source_ids:
            if source_id not in allowed_sources:
                errors.append(
                    f"{article.article_id}: source {source_id} does not "
                    "belong to the article's country"
                )

    for comment in world.comments:
        if comment.article_id not in article_ids:
            errors.append(
                f"{comment.comment_id}: comment must reference an "
                "existing article"
            )
        if comment.user_id not in user_ids:
            errors.append(
                f"{comment.comment_id}: comment must reference an existing user"
            )
        if comment.moderation_status not in _ALLOWED_MODERATION_STATUSES:
            errors.append(
                f"{comment.comment_id}: unknown moderation status "
                f"{comment.moderation_status!r}"
            )
    if world.comments:
        distinct_statuses = {
            comment.moderation_status for comment in world.comments
        }
        if len(distinct_statuses) < 2:
            errors.append(
                "comments must cover at least two distinct moderation "
                "statuses across the world"
            )

    signal_ids: set[str] = set()
    for signal in world.legal_signals:
        if signal.signal_id in signal_ids:
            errors.append(f"duplicate legal signal id: {signal.signal_id}")
        signal_ids.add(signal.signal_id)
        country_events = event_ids_by_country.get(signal.country_id)
        if country_events is None:
            errors.append(
                f"{signal.signal_id}: legal signal must reference an "
                "existing country"
            )
        elif signal.event_id not in country_events:
            errors.append(
                f"{signal.signal_id}: legal signal must reference an "
                "event from its own country"
            )
        allowed_sources = source_ids_by_country.get(signal.country_id, set())
        if signal.source_id not in allowed_sources:
            errors.append(
                f"{signal.signal_id}: legal signal must reference a "
                "source from its own country"
            )
        if any(cid not in country_ids for cid in signal.affected_country_ids):
            errors.append(
                f"{signal.signal_id}: affected_country_ids references an "
                "unknown country"
            )
        if signal.impact not in _ALLOWED_LEGAL_IMPACTS:
            errors.append(
                f"{signal.signal_id}: unknown legal signal impact "
                f"{signal.impact!r}"
            )
        if not 0 <= signal.confidence <= 100:
            errors.append(f"{signal.signal_id}: confidence is outside 0..100")

    known_locales = frozenset({"en-US", *REQUIRED_LOCALES})
    recipe_locales: set[str] = set()
    for recipe in world.document_recipes:
        if recipe.country_id not in country_ids:
            errors.append(
                f"{recipe.recipe_id}: document recipe must reference an "
                "existing country"
            )
        if recipe.locale not in known_locales:
            errors.append(
                f"{recipe.recipe_id}: unknown document recipe locale "
                f"{recipe.locale!r}"
            )
        recipe_locales.add(recipe.locale)
        if not recipe.blocks:
            errors.append(
                f"{recipe.recipe_id}: document recipe must contain at "
                "least one block"
            )
        for block in recipe.blocks:
            if not block.text.strip():
                errors.append(
                    f"{recipe.recipe_id}: block {block.block_id} resolved "
                    "to empty text"
                )
    missing_locales = set(expected_locales) - recipe_locales
    if missing_locales:
        errors.append(
            "world is missing a document recipe for locales: "
            f"{sorted(missing_locales)}"
        )

    if len(world.scenarios) < 3:
        errors.append("world must contain at least 3 scenarios")

    known_artifact_ids = (
        country_ids
        | {
            event_id
            for ids in event_ids_by_country.values()
            for event_id in ids
        }
        | {
            source_id
            for ids in source_ids_by_country.values()
            for source_id in ids
        }
        | article_ids
        | signal_ids
        | {comment.comment_id for comment in world.comments}
    )
    for scenario in world.scenarios:
        if not scenario.steps:
            errors.append(f"{scenario.scenario_id}: scenario has no steps")
        if not scenario.expected_results:
            errors.append(
                f"{scenario.scenario_id}: scenario has no expected results"
            )
        if not scenario.related_artifacts:
            errors.append(
                f"{scenario.scenario_id}: scenario has no related artifacts"
            )
        for artifact_id in scenario.related_artifacts:
            if artifact_id not in known_artifact_ids:
                errors.append(
                    f"{scenario.scenario_id}: related artifact "
                    f"{artifact_id} does not exist in the world"
                )


def ensure_world_valid(
    world: SyntheticWorld,
    *,
    forbidden_country_names: Collection[str] = (),
    expected_locales: Collection[str] = REQUIRED_LOCALES,
) -> None:
    errors = validate_world(
        world,
        forbidden_country_names=forbidden_country_names,
        expected_locales=expected_locales,
    )
    if errors:
        raise WorldValidationError("; ".join(errors))
