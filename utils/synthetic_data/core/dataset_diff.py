from __future__ import annotations

from dataclasses import dataclass
from utils.synthetic_data.core.world_models import SyntheticWorld


@dataclass(frozen=True)
class MetricChange:
    metric: str
    value_a: int
    value_b: int


@dataclass(frozen=True)
class CountryDiff:
    slug: str
    name_a: str
    name_b: str
    archetype_a: str
    archetype_b: str
    metric_changes: tuple[MetricChange, ...]


@dataclass(frozen=True)
class ScenarioCategoryDiff:
    category: str
    count_a: int
    count_b: int


@dataclass(frozen=True)
class DatasetDiff:
    dataset_id_a: str
    dataset_id_b: str
    profile_a: str
    profile_b: str
    seed_a: int
    seed_b: int
    countries_added: tuple[str, ...]
    countries_removed: tuple[str, ...]
    countries_changed: tuple[CountryDiff, ...]
    scenario_count_a: int
    scenario_count_b: int
    scenario_category_diffs: tuple[ScenarioCategoryDiff, ...]

    @property
    def is_identical(self) -> bool:
        return not (
            self.countries_added
            or self.countries_removed
            or self.countries_changed
            or self.scenario_category_diffs
            or self.scenario_count_a != self.scenario_count_b
        )


def diff_worlds(
    world_a: SyntheticWorld, world_b: SyntheticWorld
) -> DatasetDiff:
    """Compares two generated worlds (typically different seeds or
    profiles) at the level a manual QA reviewer or a regression check
    cares about: which countries were added/removed, which metrics moved
    for countries present in both, and how the scenario mix shifted —
    not a raw JSON diff, which would also churn on ids/uuids that are
    expected to differ between any two datasets."""
    countries_a = {country.slug: country for country in world_a.countries}
    countries_b = {country.slug: country for country in world_b.countries}

    countries_added = tuple(sorted(set(countries_b) - set(countries_a)))
    countries_removed = tuple(sorted(set(countries_a) - set(countries_b)))

    countries_changed: list[CountryDiff] = []
    for slug in sorted(set(countries_a) & set(countries_b)):
        country_a = countries_a[slug]
        country_b = countries_b[slug]
        metric_changes = tuple(
            MetricChange(
                metric=metric,
                value_a=country_a.current_metrics[metric],
                value_b=country_b.current_metrics[metric],
            )
            for metric in sorted(country_a.current_metrics)
            if country_a.current_metrics[metric]
            != country_b.current_metrics.get(metric)
        )
        if metric_changes or country_a.archetype != country_b.archetype:
            countries_changed.append(
                CountryDiff(
                    slug=slug,
                    name_a=country_a.name,
                    name_b=country_b.name,
                    archetype_a=country_a.archetype,
                    archetype_b=country_b.archetype,
                    metric_changes=metric_changes,
                )
            )

    category_counts_a = _scenario_category_counts(world_a)
    category_counts_b = _scenario_category_counts(world_b)
    scenario_category_diffs = tuple(
        ScenarioCategoryDiff(
            category=category,
            count_a=category_counts_a.get(category, 0),
            count_b=category_counts_b.get(category, 0),
        )
        for category in sorted(set(category_counts_a) | set(category_counts_b))
        if category_counts_a.get(category, 0)
        != category_counts_b.get(category, 0)
    )

    return DatasetDiff(
        dataset_id_a=world_a.metadata.dataset_id,
        dataset_id_b=world_b.metadata.dataset_id,
        profile_a=world_a.metadata.profile,
        profile_b=world_b.metadata.profile,
        seed_a=world_a.metadata.seed,
        seed_b=world_b.metadata.seed,
        countries_added=countries_added,
        countries_removed=countries_removed,
        countries_changed=tuple(countries_changed),
        scenario_count_a=len(world_a.scenarios),
        scenario_count_b=len(world_b.scenarios),
        scenario_category_diffs=scenario_category_diffs,
    )


def _scenario_category_counts(world: SyntheticWorld) -> dict[str, int]:
    counts: dict[str, int] = {}
    for scenario in world.scenarios:
        counts[scenario.category] = counts.get(scenario.category, 0) + 1
    return counts
