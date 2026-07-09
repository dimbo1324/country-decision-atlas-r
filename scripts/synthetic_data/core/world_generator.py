from __future__ import annotations

import hashlib
import random
import uuid
from dataclasses import dataclass
from datetime import date
from scripts.synthetic_data.core.seed import SeedFactory
from scripts.synthetic_data.core.world_input import (
    REQUIRED_METRICS,
    ArchetypeInput,
    ProfileInput,
    WorldInput,
)
from scripts.synthetic_data.core.world_models import (
    MetricSnapshot,
    SyntheticCountry,
    SyntheticEvent,
    SyntheticSource,
    SyntheticWorld,
    WorldMetadata,
)
from scripts.synthetic_data.core.world_validation import ensure_world_valid


GENERATOR_VERSION = "synthetic-world-v1"
_HISTORY_DATES = ("2024-01-01", "2025-01-01", "2026-01-01")
_SUPPORTED_LOCALES: tuple[str, ...] = ("en-US",)


@dataclass(frozen=True)
class WorldGenerationOptions:
    seed: int
    profile: str
    country_count: int | None = None
    generated_on: str | None = None


class WorldGenerator:
    def __init__(self, *, input_data: WorldInput) -> None:
        self._input_data = input_data

    def generate(self, options: WorldGenerationOptions) -> SyntheticWorld:
        profile = self._input_data.profile_by_slug(options.profile)
        country_count = (
            self._input_data.default_country_count
            if options.country_count is None
            else options.country_count
        )
        if not 4 <= country_count <= 5:
            raise ValueError("country_count must be between 4 and 5")
        if country_count > len(profile.archetypes):
            raise ValueError("profile does not define enough archetypes")

        dataset_id = self._dataset_id(options.seed)
        seed_factory = SeedFactory(options.seed)
        archetype_slugs = list(profile.archetypes)
        seed_factory.rng("profile", profile.slug).shuffle(archetype_slugs)
        used_names: set[str] = set()
        countries = tuple(
            self._generate_country(
                dataset_id=dataset_id,
                index=index,
                archetype=self._input_data.archetype_by_slug(
                    archetype_slugs[index]
                ),
                profile=profile,
                seed_factory=seed_factory,
                used_names=used_names,
            )
            for index in range(country_count)
        )
        world = SyntheticWorld(
            metadata=WorldMetadata(
                dataset_id=dataset_id,
                schema_version=self._input_data.schema_version,
                generator_version=GENERATOR_VERSION,
                seed=options.seed,
                profile=profile.slug,
                supported_locales=_SUPPORTED_LOCALES,
                source_config_checksum=self._input_data.source_checksum,
                generated_on=options.generated_on or date.today().isoformat(),
            ),
            countries=countries,
        )
        ensure_world_valid(
            world,
            forbidden_country_names=self._input_data.forbidden_country_names,
        )
        return world

    def _dataset_id(self, seed: int) -> str:
        payload = f"{seed}:{self._input_data.source_checksum}"
        return f"syn-{hashlib.sha256(payload.encode('utf-8')).hexdigest()[:16]}"

    def _generate_country(
        self,
        *,
        dataset_id: str,
        index: int,
        archetype: ArchetypeInput,
        profile: ProfileInput,
        seed_factory: SeedFactory,
        used_names: set[str],
    ) -> SyntheticCountry:
        rng = seed_factory.rng("country", str(index), archetype.slug)
        name = self._country_name(rng=rng, used_names=used_names)
        slug = name.casefold()
        country_id = str(
            uuid.uuid5(uuid.NAMESPACE_URL, f"{dataset_id}:country:{slug}")
        )
        current_metrics = {
            metric: rng.randint(
                archetype.metric_ranges[metric].minimum,
                archetype.metric_ranges[metric].maximum,
            )
            for metric in REQUIRED_METRICS
        }
        event_metric = rng.choice(REQUIRED_METRICS[:-1])
        delta = rng.randint(2, profile.event_intensity + 3)
        direction = "improved" if rng.choice((True, False)) else "declined"
        if archetype.slug == "recovering_country":
            direction = "improved"
        history = self._metric_history(
            current_metrics=current_metrics,
            event_metric=event_metric,
            direction=direction,
            delta=delta,
        )
        event = SyntheticEvent(
            event_id=f"event-{slug}-{event_metric}",
            country_id=country_id,
            as_of=_HISTORY_DATES[-1],
            metric=event_metric,
            direction=direction,
            summary=(
                f"Synthetic {direction} signal for {event_metric} in {name}."
            ),
        )
        source = SyntheticSource(
            source_id=f"source-{slug}-{event_metric}",
            country_id=country_id,
            event_id=event.event_id,
            title=f"Synthetic source for {name} {event_metric}",
            url=f"synthetic://{dataset_id}/{slug}/{event.event_id}",
            confidence=current_metrics["data_confidence"],
        )
        strengths, risks = self._strengths_and_risks(current_metrics)
        uncertainties = (
            ("data_confidence",)
            if current_metrics["data_confidence"] < 60
            else ()
        )
        return SyntheticCountry(
            country_id=country_id,
            code=f"SYN-{slug[:3].upper()}-{index + 1}",
            slug=slug,
            name=name,
            archetype=archetype.slug,
            metric_history=history,
            strengths=strengths,
            risks=risks,
            uncertainties=uncertainties,
            events=(event,),
            sources=(source,),
        )

    def _country_name(self, *, rng: random.Random, used_names: set[str]) -> str:
        forbidden_names = {
            name.casefold() for name in self._input_data.forbidden_country_names
        }
        for _ in range(100):
            prefix = rng.choice(self._input_data.name_prefixes)
            suffix = rng.choice(self._input_data.name_suffixes)
            name = f"{prefix}{suffix}"
            normalized = name.casefold()
            if normalized not in used_names | forbidden_names:
                used_names.add(normalized)
                return name
        raise ValueError("could not generate a unique synthetic country name")

    @staticmethod
    def _metric_history(
        *,
        current_metrics: dict[str, int],
        event_metric: str,
        direction: str,
        delta: int,
    ) -> tuple[MetricSnapshot, ...]:
        current = current_metrics.copy()
        midpoint = current.copy()
        previous = current.copy()
        direction_factor = 1 if direction == "improved" else -1
        midpoint[event_metric] = max(
            0, min(100, current[event_metric] - direction_factor * (delta // 2))
        )
        previous[event_metric] = max(
            0, min(100, current[event_metric] - direction_factor * delta)
        )
        return (
            MetricSnapshot(as_of=_HISTORY_DATES[0], metrics=previous),
            MetricSnapshot(as_of=_HISTORY_DATES[1], metrics=midpoint),
            MetricSnapshot(as_of=_HISTORY_DATES[2], metrics=current),
        )

    @staticmethod
    def _strengths_and_risks(
        metrics: dict[str, int],
    ) -> tuple[tuple[str, ...], tuple[str, ...]]:
        ordered = sorted(metrics, key=metrics.__getitem__)
        risks = tuple(metric for metric in ordered if metrics[metric] <= 45)[:2]
        strengths = tuple(
            metric for metric in reversed(ordered) if metrics[metric] >= 65
        )[:2]
        return strengths or (ordered[-1],), risks or (ordered[0],)
