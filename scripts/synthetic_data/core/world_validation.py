from __future__ import annotations

from collections.abc import Collection
from scripts.synthetic_data.core.world_input import REQUIRED_METRICS
from scripts.synthetic_data.core.world_models import SyntheticWorld


class WorldValidationError(RuntimeError):
    pass


def validate_world(
    world: SyntheticWorld,
    *,
    forbidden_country_names: Collection[str] = (),
) -> tuple[str, ...]:
    errors: list[str] = []
    country_ids: set[str] = set()
    country_codes: set[str] = set()
    country_slugs: set[str] = set()
    country_names: set[str] = set()
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
        for source in country.sources:
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

    return tuple(errors)


def ensure_world_valid(
    world: SyntheticWorld,
    *,
    forbidden_country_names: Collection[str] = (),
) -> None:
    errors = validate_world(
        world, forbidden_country_names=forbidden_country_names
    )
    if errors:
        raise WorldValidationError("; ".join(errors))
