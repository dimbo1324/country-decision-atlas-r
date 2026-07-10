from app.repositories import methodology_config as repository
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from psycopg import Connection
from time import monotonic
from typing import Any


ACTIVE_METHODOLOGY_VERSION = "v1.0"
METHODOLOGY_CACHE_TTL_SECONDS = 60.0

SCORE_LABEL_WEAK_BELOW = "score_label.weak_below"
SCORE_LABEL_LIMITED_BELOW = "score_label.limited_below"
SCORE_LABEL_MODERATE_BELOW = "score_label.moderate_below"
SCORE_LABEL_STRONG_BELOW = "score_label.strong_below"
STRENGTH_MIN_SCORE = "strength.min_score"
WEAKNESS_MAX_SCORE = "weakness.max_score"
CONFIDENCE_HIGH_MIN_AVERAGE = "confidence.high_min_average"
CONFIDENCE_MEDIUM_MIN_AVERAGE = "confidence.medium_min_average"
RECOMMENDATION_TIE_DELTA_BELOW = "recommendation.tie_delta_below"
RECOMMENDATION_MEDIUM_CONFIDENCE_DELTA_BELOW = (
    "recommendation.medium_confidence_delta_below"
)
BOARD_MAX_ACTIVE_POSTS = "board.max_active_posts"
BOARD_MAX_CONTACT_REQUESTS_PER_DAY = "board.max_contact_requests_per_day"
BOARD_MAX_REPORTS_PER_DAY = "board.max_reports_per_day"
BOARD_AUTO_HIDE_REPORT_THRESHOLD = "board.auto_hide_report_threshold"
BOARD_MAX_THREAD_MESSAGES_PER_DAY = "board.max_thread_messages_per_day"
FLOWS_K_ANONYMITY = "flows.k_anonymity"
TRIP_WARNING_HIGH_IMPACT_MIN_RANK = "trip.warning.high_impact_min_rank"
TRIP_WARNING_RESTRICTIVE_PAIR_SEVERITY_RANK = (
    "trip.warning.restrictive_pair_severity_rank"
)
TRIP_WARNING_MISSING_PAIR_SEVERITY_RANK = (
    "trip.warning.missing_pair_severity_rank"
)
AUTHOR_METRICS_MIN_METHODOLOGY_LENGTH = "author_metrics.min_methodology_length"
AUTHOR_METRICS_MIN_COUNTRY_COVERAGE = "author_metrics.min_country_coverage"
RETENTION_ANALYTICS_DAYS = "retention.analytics_days"
RETENTION_DOMAIN_EVENTS_DAYS = "retention.domain_events_days"
RETENTION_SESSIONS_DAYS = "retention.sessions_days"

REQUIRED_NUMERIC_KEYS = (
    SCORE_LABEL_WEAK_BELOW,
    SCORE_LABEL_LIMITED_BELOW,
    SCORE_LABEL_MODERATE_BELOW,
    SCORE_LABEL_STRONG_BELOW,
    STRENGTH_MIN_SCORE,
    WEAKNESS_MAX_SCORE,
    CONFIDENCE_HIGH_MIN_AVERAGE,
    CONFIDENCE_MEDIUM_MIN_AVERAGE,
    RECOMMENDATION_TIE_DELTA_BELOW,
    RECOMMENDATION_MEDIUM_CONFIDENCE_DELTA_BELOW,
    BOARD_MAX_ACTIVE_POSTS,
    BOARD_MAX_CONTACT_REQUESTS_PER_DAY,
    BOARD_MAX_REPORTS_PER_DAY,
    BOARD_AUTO_HIDE_REPORT_THRESHOLD,
    BOARD_MAX_THREAD_MESSAGES_PER_DAY,
    FLOWS_K_ANONYMITY,
    TRIP_WARNING_HIGH_IMPACT_MIN_RANK,
    TRIP_WARNING_RESTRICTIVE_PAIR_SEVERITY_RANK,
    TRIP_WARNING_MISSING_PAIR_SEVERITY_RANK,
    AUTHOR_METRICS_MIN_METHODOLOGY_LENGTH,
    AUTHOR_METRICS_MIN_COUNTRY_COVERAGE,
    RETENTION_ANALYTICS_DAYS,
    RETENTION_DOMAIN_EVENTS_DAYS,
    RETENTION_SESSIONS_DAYS,
)


class MethodologyConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class MethodologyParameter:
    id: str
    version: str
    param_key: str
    value_numeric: Decimal | None
    value_json: Any | None
    description: str
    effective_from: datetime
    created_at: datetime


@dataclass(frozen=True)
class ScoreLabelThresholds:
    weak_below: float
    limited_below: float
    moderate_below: float
    strong_below: float


@dataclass(frozen=True)
class ConfidenceThresholds:
    high_min_average: float
    medium_min_average: float


@dataclass(frozen=True)
class RecommendationThresholds:
    tie_delta_below: float
    medium_confidence_delta_below: float


@dataclass(frozen=True)
class DecisionThresholds:
    strength_min_score: float
    weakness_max_score: float
    confidence: ConfidenceThresholds
    recommendation: RecommendationThresholds


@dataclass(frozen=True)
class BoardLimits:
    max_active_posts: int
    max_contact_requests_per_day: int
    max_reports_per_day: int
    auto_hide_report_threshold: int
    max_thread_messages_per_day: int


@dataclass(frozen=True)
class TripWarningThresholds:
    high_impact_min_rank: int
    restrictive_pair_severity_rank: int
    missing_pair_severity_rank: int


@dataclass(frozen=True)
class AuthorMetricsThresholds:
    min_methodology_length: int
    min_country_coverage: int


@dataclass(frozen=True)
class RetentionThresholds:
    analytics_days: int
    domain_events_days: int
    sessions_days: int


@dataclass(frozen=True)
class MethodologyConfig:
    version: str
    parameters: dict[str, MethodologyParameter]
    score_labels: ScoreLabelThresholds
    decision: DecisionThresholds
    board: BoardLimits
    flows_k_anonymity: int
    trip_warnings: TripWarningThresholds
    author_metrics: AuthorMetricsThresholds
    retention: RetentionThresholds


_cached_config: MethodologyConfig | None = None
_cached_at: float | None = None


def clear_methodology_config_cache() -> None:
    global _cached_at, _cached_config
    _cached_config = None
    _cached_at = None


def get_active_methodology_config(
    connection: Connection[Any],
) -> MethodologyConfig:
    global _cached_at, _cached_config
    now = monotonic()
    if (
        _cached_config is not None
        and _cached_at is not None
        and now - _cached_at < METHODOLOGY_CACHE_TTL_SECONDS
    ):
        return _cached_config
    version = repository.get_active_methodology_version(connection)
    if version is None:
        raise MethodologyConfigError("Active methodology version is missing.")
    rows = repository.list_parameters_for_version(connection, version)
    config = build_methodology_config(version, rows)
    _cached_config = config
    _cached_at = now
    return config


def build_methodology_config(
    version: str, rows: list[dict[str, Any]]
) -> MethodologyConfig:
    parameters = {
        str(row["param_key"]): _parameter_from_row(row) for row in rows
    }
    missing = [
        param_key
        for param_key in REQUIRED_NUMERIC_KEYS
        if param_key not in parameters
        or parameters[param_key].value_numeric is None
    ]
    if missing:
        raise MethodologyConfigError(
            f"Methodology version {version} is missing parameters: {', '.join(missing)}."
        )
    score_labels = ScoreLabelThresholds(
        weak_below=_numeric(parameters, SCORE_LABEL_WEAK_BELOW),
        limited_below=_numeric(parameters, SCORE_LABEL_LIMITED_BELOW),
        moderate_below=_numeric(parameters, SCORE_LABEL_MODERATE_BELOW),
        strong_below=_numeric(parameters, SCORE_LABEL_STRONG_BELOW),
    )
    decision = DecisionThresholds(
        strength_min_score=_numeric(parameters, STRENGTH_MIN_SCORE),
        weakness_max_score=_numeric(parameters, WEAKNESS_MAX_SCORE),
        confidence=ConfidenceThresholds(
            high_min_average=_numeric(parameters, CONFIDENCE_HIGH_MIN_AVERAGE),
            medium_min_average=_numeric(
                parameters, CONFIDENCE_MEDIUM_MIN_AVERAGE
            ),
        ),
        recommendation=RecommendationThresholds(
            tie_delta_below=_numeric(
                parameters, RECOMMENDATION_TIE_DELTA_BELOW
            ),
            medium_confidence_delta_below=_numeric(
                parameters, RECOMMENDATION_MEDIUM_CONFIDENCE_DELTA_BELOW
            ),
        ),
    )
    board = BoardLimits(
        max_active_posts=_positive_int(parameters, BOARD_MAX_ACTIVE_POSTS),
        max_contact_requests_per_day=_positive_int(
            parameters, BOARD_MAX_CONTACT_REQUESTS_PER_DAY
        ),
        max_reports_per_day=_positive_int(
            parameters, BOARD_MAX_REPORTS_PER_DAY
        ),
        auto_hide_report_threshold=_positive_int(
            parameters, BOARD_AUTO_HIDE_REPORT_THRESHOLD
        ),
        max_thread_messages_per_day=_positive_int(
            parameters, BOARD_MAX_THREAD_MESSAGES_PER_DAY
        ),
    )
    flows_k_anonymity = _positive_int(parameters, FLOWS_K_ANONYMITY)
    trip_warnings = TripWarningThresholds(
        high_impact_min_rank=_severity_rank(
            parameters, TRIP_WARNING_HIGH_IMPACT_MIN_RANK
        ),
        restrictive_pair_severity_rank=_severity_rank(
            parameters, TRIP_WARNING_RESTRICTIVE_PAIR_SEVERITY_RANK
        ),
        missing_pair_severity_rank=_severity_rank(
            parameters, TRIP_WARNING_MISSING_PAIR_SEVERITY_RANK
        ),
    )
    author_metrics = AuthorMetricsThresholds(
        min_methodology_length=_positive_int(
            parameters, AUTHOR_METRICS_MIN_METHODOLOGY_LENGTH
        ),
        min_country_coverage=_positive_int(
            parameters, AUTHOR_METRICS_MIN_COUNTRY_COVERAGE
        ),
    )
    retention = RetentionThresholds(
        analytics_days=_positive_int(parameters, RETENTION_ANALYTICS_DAYS),
        domain_events_days=_positive_int(
            parameters, RETENTION_DOMAIN_EVENTS_DAYS
        ),
        sessions_days=_positive_int(parameters, RETENTION_SESSIONS_DAYS),
    )
    _validate_thresholds(score_labels, decision)
    return MethodologyConfig(
        version=version,
        parameters=parameters,
        score_labels=score_labels,
        decision=decision,
        board=board,
        flows_k_anonymity=flows_k_anonymity,
        trip_warnings=trip_warnings,
        author_metrics=author_metrics,
        retention=retention,
    )


def list_active_parameters(
    connection: Connection[Any],
) -> tuple[str, list[MethodologyParameter]]:
    config = get_active_methodology_config(connection)
    return config.version, [
        config.parameters[key] for key in sorted(config.parameters)
    ]


def _parameter_from_row(row: dict[str, Any]) -> MethodologyParameter:
    raw_numeric = row.get("value_numeric")
    return MethodologyParameter(
        id=str(row["id"]),
        version=str(row["version"]),
        param_key=str(row["param_key"]),
        value_numeric=Decimal(str(raw_numeric))
        if raw_numeric is not None
        else None,
        value_json=row.get("value_json"),
        description=str(row["description"]),
        effective_from=row["effective_from"],
        created_at=row["created_at"],
    )


def _numeric(
    parameters: dict[str, MethodologyParameter], param_key: str
) -> float:
    value = parameters[param_key].value_numeric
    if value is None:
        raise MethodologyConfigError(
            f"Methodology parameter {param_key} must be numeric."
        )
    return float(value)


def _positive_int(
    parameters: dict[str, MethodologyParameter], param_key: str
) -> int:
    value = _numeric(parameters, param_key)
    if value < 1 or value != int(value):
        raise MethodologyConfigError(
            f"Methodology parameter {param_key} must be a positive integer."
        )
    return int(value)


def _severity_rank(
    parameters: dict[str, MethodologyParameter], param_key: str
) -> int:
    value = _positive_int(parameters, param_key)
    if value > 4:
        raise MethodologyConfigError(
            f"Methodology parameter {param_key} must be a severity rank within 1..4."
        )
    return value


def _validate_thresholds(
    score_labels: ScoreLabelThresholds, decision: DecisionThresholds
) -> None:
    values = (
        score_labels.weak_below,
        score_labels.limited_below,
        score_labels.moderate_below,
        score_labels.strong_below,
    )
    if not all(0 <= value <= 100 for value in values):
        raise MethodologyConfigError(
            "Score label thresholds must stay within 0..100."
        )
    if not values == tuple(sorted(values)) or len(set(values)) != len(values):
        raise MethodologyConfigError(
            "Score label thresholds must be strictly increasing."
        )
    if decision.weakness_max_score >= decision.strength_min_score:
        raise MethodologyConfigError(
            "weakness.max_score must be strictly below strength.min_score."
        )
    confidence = decision.confidence
    if not (
        1 <= confidence.medium_min_average < confidence.high_min_average <= 3
    ):
        raise MethodologyConfigError(
            "Confidence thresholds must be ordered within 1..3."
        )
    recommendation = decision.recommendation
    if not (
        0
        < recommendation.tie_delta_below
        < recommendation.medium_confidence_delta_below
    ):
        raise MethodologyConfigError(
            "Recommendation deltas must be positive and ordered."
        )
