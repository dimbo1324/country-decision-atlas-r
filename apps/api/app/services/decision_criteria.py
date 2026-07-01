from dataclasses import dataclass


@dataclass(frozen=True)
class DecisionCriterionDefinition:
    slug: str
    label_ru: str
    label_en: str


DECISION_CRITERION_DEFINITIONS = (
    DecisionCriterionDefinition(
        slug="legalization_score",
        label_ru="Легализация",
        label_en="Legalization",
    ),
    DecisionCriterionDefinition(
        slug="long_term_status_score",
        label_ru="Долгосрочный статус",
        label_en="Long-term status",
    ),
    DecisionCriterionDefinition(
        slug="cost_of_living_score",
        label_ru="Стоимость жизни",
        label_en="Cost of living",
    ),
    DecisionCriterionDefinition(
        slug="safety_score",
        label_ru="Безопасность",
        label_en="Safety",
    ),
    DecisionCriterionDefinition(
        slug="business_score",
        label_ru="Бизнес",
        label_en="Business",
    ),
    DecisionCriterionDefinition(
        slug="legal_stability_score",
        label_ru="Правовая стабильность",
        label_en="Legal stability",
    ),
    DecisionCriterionDefinition(
        slug="source_quality_score",
        label_ru="Качество источников",
        label_en="Source quality",
    ),
)

DECISION_CRITERIA = tuple(
    definition.slug for definition in DECISION_CRITERION_DEFINITIONS
)
DECISION_CRITERIA_BY_SLUG = {
    definition.slug: definition for definition in DECISION_CRITERION_DEFINITIONS
}


def list_decision_criterion_metadata_issues() -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    seen: set[str] = set()
    for definition in DECISION_CRITERION_DEFINITIONS:
        if definition.slug in seen:
            issues.append({"criterion": definition.slug, "reason": "duplicate_slug"})
        seen.add(definition.slug)
        if not definition.label_ru:
            issues.append({"criterion": definition.slug, "reason": "missing_label_ru"})
        if not definition.label_en:
            issues.append({"criterion": definition.slug, "reason": "missing_label_en"})
    for slug in DECISION_CRITERIA:
        if slug not in DECISION_CRITERIA_BY_SLUG:
            issues.append({"criterion": slug, "reason": "missing_definition"})
    return issues
