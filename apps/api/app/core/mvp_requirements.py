from typing import Any


MVP_COUNTRY_SLUGS = ("russia", "uruguay", "argentina")
ONBOARDING_COUNTRY_SLUGS: tuple[str, ...] = ()
MVP_SCENARIO_SLUGS = (
    "relocation_residence",
    "permanent_residence_citizenship",
    "low_budget_living",
    "business_self_employment",
    "safety_political_risk",
)

MVP_READINESS_THRESHOLDS: dict[str, Any] = {
    "required_cii_metrics": 6,
    "required_scenario_scores": 5,
    "minimum_sources": 10,
    "minimum_evidence_items": 15,
    "minimum_legal_signals": 5,
    "minimum_timeline_events": 5,
    "timeline_events_with_source_ratio": 1.0,
    "country_card_required": True,
    "localization_metadata_required": True,
    "matrix_ready_required": True,
    "home_overview_ready_required": True,
}

MVP_CONTENT_DEPTH_TARGETS = {
    "published_sources": 15,
    "published_evidence_items": 20,
    "published_legal_signals": 8,
}
