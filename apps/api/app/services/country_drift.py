from app.repositories import (
    country_drift as country_drift_repo,
    domain_events as domain_events_repo,
)
from app.services.country_drift_methodology import (
    IMPACT_DIRECTIONS,
    LABEL_INSUFFICIENT_DATA,
    METHODOLOGY_VERSION,
    WINDOW_DAYS,
    build_drift_input_summary,
    compute_net_score,
    confidence_for_drift,
    impact_level_weight,
    label_for_drift,
)
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from psycopg import Connection
from typing import Any
from uuid import UUID


class CountryDriftCountryNotFoundError(ValueError):
    pass


@dataclass(frozen=True)
class CountryDriftInputEvent:
    event_id: str | None
    legal_signal_id: str | None
    impact_direction: str
    impact_level: str


@dataclass
class CountryDriftWeights:
    positive: Decimal = Decimal("0")
    negative: Decimal = Decimal("0")
    neutral: Decimal = Decimal("0")
    mixed: Decimal = Decimal("0")
    uncertain: Decimal = Decimal("0")

    @property
    def total(self) -> Decimal:
        return (
            self.positive
            + self.negative
            + self.neutral
            + self.mixed
            + self.uncertain
        )


@dataclass
class CountryDriftCounts:
    positive: int = 0
    negative: int = 0
    neutral: int = 0
    mixed: int = 0
    uncertain: int = 0

    @property
    def total(self) -> int:
        return (
            self.positive
            + self.negative
            + self.neutral
            + self.mixed
            + self.uncertain
        )


@dataclass
class CountryDriftCalculationResult:
    label: str
    confidence: str
    net_score: Decimal | None
    positive_weight: Decimal
    negative_weight: Decimal
    neutral_weight: Decimal
    mixed_weight: Decimal
    uncertain_weight: Decimal
    total_weight: Decimal
    event_count: int
    positive_count: int
    negative_count: int
    neutral_count: int
    mixed_count: int
    uncertain_count: int
    input_summary: dict[str, Any]
    methodology_version: str
    window_days: int


@dataclass
class CountryDriftSnapshotDraft:
    country_id: str
    country_slug: str
    period_start: date
    period_end: date
    window_days: int
    label: str
    previous_label: str | None
    confidence: str
    net_score: Decimal | None
    positive_weight: Decimal
    negative_weight: Decimal
    neutral_weight: Decimal
    mixed_weight: Decimal
    uncertain_weight: Decimal
    total_weight: Decimal
    event_count: int
    positive_count: int
    negative_count: int
    neutral_count: int
    mixed_count: int
    uncertain_count: int
    methodology_version: str
    input_summary: dict[str, Any]


@dataclass
class CountryDriftStoredResult:
    country_slug: str
    country_not_found: bool = False
    dry_run: bool = False
    computed: bool = False
    stored: bool = False
    label: str | None = None
    previous_label: str | None = None
    confidence: str | None = None
    net_score: Decimal | None = None
    event_count: int = 0
    event_emitted: bool = False
    error: str | None = None


@dataclass
class CountryDriftBatchResult:
    countries_processed: int = 0
    snapshots_written: int = 0
    events_emitted: int = 0
    insufficient_data_count: int = 0
    errors: list[dict[str, Any]] = field(default_factory=list)


def _now() -> datetime:
    return datetime.now(tz=UTC)


def _parse_event(row: Mapping[str, Any]) -> CountryDriftInputEvent:
    event_id = row.get("event_id")
    legal_signal_id = row.get("legal_signal_id")
    return CountryDriftInputEvent(
        event_id=str(event_id) if event_id is not None else None,
        legal_signal_id=str(legal_signal_id)
        if legal_signal_id is not None
        else None,
        impact_direction=str(row["impact_direction"]),
        impact_level=str(row["impact_level"]),
    )


def calculate_country_drift(
    events: Sequence[Mapping[str, Any]],
    *,
    window_days: int = WINDOW_DAYS,
    methodology_version: str = METHODOLOGY_VERSION,
) -> CountryDriftCalculationResult:
    weights = CountryDriftWeights()
    counts = CountryDriftCounts()
    event_ids: list[str] = []
    legal_signal_ids: list[str] = []

    for row in events:
        parsed = _parse_event(row)
        if parsed.impact_direction not in IMPACT_DIRECTIONS:
            raise ValueError(
                f"unknown impact_direction: {parsed.impact_direction}"
            )
        weight = impact_level_weight(parsed.impact_level)

        if parsed.impact_direction == "positive":
            weights.positive += weight
            counts.positive += 1
        elif parsed.impact_direction == "negative":
            weights.negative += weight
            counts.negative += 1
        elif parsed.impact_direction == "neutral":
            weights.neutral += weight
            counts.neutral += 1
        elif parsed.impact_direction == "mixed":
            weights.mixed += weight
            counts.mixed += 1
        else:
            weights.uncertain += weight
            counts.uncertain += 1

        if parsed.event_id is not None:
            event_ids.append(parsed.event_id)
        if parsed.legal_signal_id is not None:
            legal_signal_ids.append(parsed.legal_signal_id)

    event_count = counts.total
    net_score = compute_net_score(
        weights.positive,
        weights.negative,
        weights.neutral,
        weights.mixed,
        weights.uncertain,
    )
    label = label_for_drift(event_count, net_score)
    confidence = confidence_for_drift(
        event_count, counts.mixed, counts.uncertain
    )

    input_summary = build_drift_input_summary(
        window_days=window_days,
        event_ids=event_ids,
        legal_signal_ids=legal_signal_ids,
    )
    input_summary["direction_counts"] = {
        "positive": counts.positive,
        "negative": counts.negative,
        "neutral": counts.neutral,
        "mixed": counts.mixed,
        "uncertain": counts.uncertain,
    }

    return CountryDriftCalculationResult(
        label=label,
        confidence=confidence,
        net_score=net_score,
        positive_weight=weights.positive,
        negative_weight=weights.negative,
        neutral_weight=weights.neutral,
        mixed_weight=weights.mixed,
        uncertain_weight=weights.uncertain,
        total_weight=weights.total,
        event_count=event_count,
        positive_count=counts.positive,
        negative_count=counts.negative,
        neutral_count=counts.neutral,
        mixed_count=counts.mixed,
        uncertain_count=counts.uncertain,
        input_summary=input_summary,
        methodology_version=methodology_version,
        window_days=window_days,
    )


def build_drift_period(
    *,
    period_end: date | None = None,
    window_days: int = WINDOW_DAYS,
) -> tuple[date, date]:
    if window_days <= 0:
        raise ValueError("window_days must be > 0")
    resolved_period_end = period_end or date.today()
    resolved_period_start = resolved_period_end - timedelta(
        days=window_days - 1
    )
    return resolved_period_start, resolved_period_end


def compute_country_drift_snapshot(
    conn: Connection[Any],
    *,
    country_slug: str,
    period_end: date | None = None,
    window_days: int = WINDOW_DAYS,
) -> CountryDriftSnapshotDraft:
    country = country_drift_repo.get_country_for_drift(conn, country_slug)
    if country is None:
        raise CountryDriftCountryNotFoundError(country_slug)

    period_start, resolved_period_end = build_drift_period(
        period_end=period_end, window_days=window_days
    )
    events = country_drift_repo.list_drift_input_events(
        conn, country_slug, period_start, resolved_period_end
    )
    result = calculate_country_drift(events, window_days=window_days)

    previous_snapshot = country_drift_repo.get_previous_drift_snapshot(
        conn, country["id"], resolved_period_end, result.methodology_version
    )
    previous_label = previous_snapshot["label"] if previous_snapshot else None

    return CountryDriftSnapshotDraft(
        country_id=country["id"],
        country_slug=country["slug"],
        period_start=period_start,
        period_end=resolved_period_end,
        window_days=window_days,
        label=result.label,
        previous_label=previous_label,
        confidence=result.confidence,
        net_score=result.net_score,
        positive_weight=result.positive_weight,
        negative_weight=result.negative_weight,
        neutral_weight=result.neutral_weight,
        mixed_weight=result.mixed_weight,
        uncertain_weight=result.uncertain_weight,
        total_weight=result.total_weight,
        event_count=result.event_count,
        positive_count=result.positive_count,
        negative_count=result.negative_count,
        neutral_count=result.neutral_count,
        mixed_count=result.mixed_count,
        uncertain_count=result.uncertain_count,
        methodology_version=result.methodology_version,
        input_summary=result.input_summary,
    )


def _should_emit_drift_changed(draft: CountryDriftSnapshotDraft) -> bool:
    if draft.previous_label is None:
        return False
    if draft.label == draft.previous_label:
        return False
    return draft.label != LABEL_INSUFFICIENT_DATA


def _drift_changed_event_key(draft: CountryDriftSnapshotDraft) -> str:
    return (
        f"country:{draft.country_slug}:drift.changed:"
        f"{draft.period_end.isoformat()}:{draft.methodology_version}"
    )


def _drift_changed_payload(draft: CountryDriftSnapshotDraft) -> dict[str, Any]:
    return {
        "country_slug": draft.country_slug,
        "event_type": "drift.changed",
        "previous_label": draft.previous_label,
        "new_label": draft.label,
        "period_start": draft.period_start.isoformat(),
        "period_end": draft.period_end.isoformat(),
        "window_days": draft.window_days,
        "net_score": float(draft.net_score)
        if draft.net_score is not None
        else None,
        "confidence": draft.confidence,
        "event_count": draft.event_count,
        "methodology_version": draft.methodology_version,
        "positive_count": draft.positive_count,
        "negative_count": draft.negative_count,
        "neutral_count": draft.neutral_count,
        "mixed_count": draft.mixed_count,
        "uncertain_count": draft.uncertain_count,
    }


def _emit_drift_changed(
    conn: Connection[Any], draft: CountryDriftSnapshotDraft
) -> dict[str, Any] | None:
    return domain_events_repo.insert_domain_event(
        conn,
        event_key=_drift_changed_event_key(draft),
        event_type="drift.changed",
        aggregate_type="country",
        aggregate_id=UUID(draft.country_id),
        country_slug=draft.country_slug,
        payload=_drift_changed_payload(draft),
        status="pending",
        notifiable=True,
    )


def compute_and_store_country_drift(
    conn: Connection[Any],
    *,
    country_slug: str,
    period_end: date | None = None,
    window_days: int = WINDOW_DAYS,
    emit_events: bool = True,
    dry_run: bool = False,
) -> CountryDriftStoredResult:
    result = CountryDriftStoredResult(
        country_slug=country_slug, dry_run=dry_run
    )

    try:
        draft = compute_country_drift_snapshot(
            conn,
            country_slug=country_slug,
            period_end=period_end,
            window_days=window_days,
        )
    except CountryDriftCountryNotFoundError:
        result.country_not_found = True
        return result
    except Exception as exc:
        conn.rollback()
        result.error = str(exc)
        return result

    result.computed = True
    result.label = draft.label
    result.previous_label = draft.previous_label
    result.confidence = draft.confidence
    result.net_score = draft.net_score
    result.event_count = draft.event_count

    if dry_run:
        result.event_emitted = emit_events and _should_emit_drift_changed(draft)
        return result

    try:
        country_drift_repo.upsert_drift_snapshot(
            conn,
            country_id=draft.country_id,
            period_start=draft.period_start,
            period_end=draft.period_end,
            window_days=draft.window_days,
            label=draft.label,
            previous_label=draft.previous_label,
            confidence=draft.confidence,
            net_score=draft.net_score,
            positive_weight=draft.positive_weight,
            negative_weight=draft.negative_weight,
            neutral_weight=draft.neutral_weight,
            mixed_weight=draft.mixed_weight,
            uncertain_weight=draft.uncertain_weight,
            total_weight=draft.total_weight,
            event_count=draft.event_count,
            positive_count=draft.positive_count,
            negative_count=draft.negative_count,
            neutral_count=draft.neutral_count,
            mixed_count=draft.mixed_count,
            uncertain_count=draft.uncertain_count,
            methodology_version=draft.methodology_version,
            input_summary=draft.input_summary,
            computed_at=_now(),
            expires_at=None,
        )
        result.stored = True
        if emit_events and _should_emit_drift_changed(draft):
            emitted_row = _emit_drift_changed(conn, draft)
            result.event_emitted = emitted_row is not None
    except Exception as exc:
        conn.rollback()
        result.error = str(exc)

    return result


def compute_and_store_all_country_drifts(
    conn: Connection[Any],
    *,
    period_end: date | None = None,
    window_days: int = WINDOW_DAYS,
    emit_events: bool = True,
    dry_run: bool = False,
) -> CountryDriftBatchResult:
    summary = CountryDriftBatchResult()
    countries = country_drift_repo.list_countries_for_drift(conn)
    for country in countries:
        slug = country["slug"]
        result = compute_and_store_country_drift(
            conn,
            country_slug=slug,
            period_end=period_end,
            window_days=window_days,
            emit_events=emit_events,
            dry_run=dry_run,
        )
        summary.countries_processed += 1
        if result.stored:
            summary.snapshots_written += 1
        if result.event_emitted:
            summary.events_emitted += 1
        if result.label == LABEL_INSUFFICIENT_DATA:
            summary.insufficient_data_count += 1
        if result.error:
            summary.errors.append({"country_slug": slug, "error": result.error})
    return summary
