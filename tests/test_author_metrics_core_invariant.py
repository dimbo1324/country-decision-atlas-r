"""Core invariant: author metrics never mix into platform CII/decision/compare surfaces.

Enforced two ways: a static import-boundary scan over the core-math modules, and a
response-identity check proving a decision run is byte-identical whether or not
author-metrics data would be present, because those code paths never call into
services.author_metrics in the first place.
"""

from app.schemas.decision_engine import DecisionRunRequest
from app.services import decision_engine
from pathlib import Path
from psycopg import Connection
from tests.test_decision_run import install_repository_fakes, payload
from typing import Any, cast


CORE_MATH_MODULES = [
    "app/services/cii.py",
    "app/services/cii_comparison.py",
    "app/services/cii_matrix.py",
    "app/services/decision_analytics.py",
    "app/services/decision_criteria.py",
    "app/services/decision_labels.py",
    "app/services/decision_origin_context.py",
    "app/services/decision_passports.py",
    "app/services/decision_personalization.py",
    "app/services/decision_warnings.py",
    "app/services/decision_wizard.py",
    "app/services/persona_runtime.py",
    "app/services/persona_weights.py",
    "app/services/scenario_risk.py",
    "app/api/v1/decision.py",
    "app/api/v1/decision_passports.py",
    "app/api/v1/countries.py",
    "app/api/v1/country_pairs.py",
]


def test_core_math_modules_never_import_author_metrics() -> None:
    for relative_path in CORE_MATH_MODULES:
        source = Path("apps/api", relative_path).read_text(encoding="utf-8")
        assert "author_metrics" not in source, (
            f"{relative_path} must never import or reference author_metrics"
        )


def test_decision_engine_directory_never_imports_author_metrics() -> None:
    decision_engine_dir = Path("apps/api/app/services/decision_engine")
    for module_path in decision_engine_dir.glob("*.py"):
        source = module_path.read_text(encoding="utf-8")
        assert "author_metrics" not in source, (
            f"{module_path} must never import or reference author_metrics"
        )


def test_decision_run_response_is_identical_regardless_of_author_metrics_data(
    monkeypatch: Any,
) -> None:
    install_repository_fakes(monkeypatch)
    connection = cast(Connection[Any], object())

    baseline = decision_engine.run_decision(connection, payload()).model_dump(
        mode="json"
    )

    def _raise_if_called(*_a: Any, **_kw: Any) -> Any:
        raise AssertionError(
            "decision_engine must never call into author_metrics repositories"
        )

    from app.repositories import author_metrics as author_metrics_repository

    for name in (
        "list_published_definitions_for_country",
        "list_published_definitions_for_author",
        "get_definition_by_id",
    ):
        monkeypatch.setattr(author_metrics_repository, name, _raise_if_called)

    after_seeding_guard = decision_engine.run_decision(
        connection, payload()
    ).model_dump(mode="json")

    baseline["meta"].pop("generated_at", None)
    after_seeding_guard["meta"].pop("generated_at", None)
    assert baseline == after_seeding_guard


def test_decision_run_request_schema_has_no_author_metrics_fields() -> None:
    fields = set(DecisionRunRequest.model_fields)
    assert not any("author" in field for field in fields)
