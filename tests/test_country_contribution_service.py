"""Country contribution service: proposal lifecycle, ownership scoping, curator gate, scenario scores."""

import pytest
from app.core.auth import CurrentUser
from app.repositories import (
    admin_content as admin_content_repository,
    country_contribution as repository,
)
from app.schemas.country_contribution import (
    ContributorSourceCreate,
    CountryMetricValueEntry,
    CountryProposalCreate,
    CountryProposalPatch,
    ScenarioBreakdownEntry,
)
from app.services import feature_flags as feature_flags_service
from app.services.country_contribution import (
    content as content_service,
    curation as curation_service,
    helpers,
    proposals as proposals_service,
    scores as scores_service,
)
from fastapi import HTTPException
from psycopg import Connection
from typing import Any, cast
from unittest.mock import MagicMock


CONNECTION = cast(Connection[Any], MagicMock())
PROPOSER_ID = "11111111-1111-1111-1111-111111111111"
OTHER_USER_ID = "22222222-2222-2222-2222-222222222222"
EDITOR_ID = "33333333-3333-3333-3333-333333333333"
COUNTRY_ID = "44444444-4444-4444-4444-444444444444"
PROPOSAL_ID = "55555555-5555-5555-5555-555555555555"

CONTRIBUTOR = CurrentUser(
    id=PROPOSER_ID,
    email="contributor@example.local",
    display_name="Contributor",
    role="user",
    status="active",
)
EDITOR = CurrentUser(
    id=EDITOR_ID,
    email="editor@example.local",
    display_name="Editor",
    role="editor",
    status="active",
)


def _proposal(**overrides: Any) -> dict[str, Any]:
    row = {
        "id": PROPOSAL_ID,
        "proposer_user_id": PROPOSER_ID,
        "country_id": COUNTRY_ID,
        "slug": "wakanda",
        "name_en": "Wakanda",
        "name_ru": "Ваканда",
        "iso2": "WK",
        "iso3": "WKD",
        "justification": "x" * 30,
        "status": "draft",
        "curator_user_id": None,
        "readiness_snapshot": None,
        "moderated_by": None,
        "moderated_at": None,
        "moderation_reason": None,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "published_at": None,
        "country_is_active": False,
        "country_is_demo": False,
    }
    row.update(overrides)
    return row


def _enable_feature(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        feature_flags_service, "is_feature_enabled_by_key", lambda *_: True
    )


def _assert_error(exc: pytest.ExceptionInfo[HTTPException], code: str) -> None:
    detail = cast(dict[str, Any], exc.value.detail)
    assert detail["error"]["code"] == code


class TestProposalCreation:
    def test_create_rejects_taken_slug(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_feature(monkeypatch)
        monkeypatch.setattr(repository, "country_slug_exists", lambda *_: True)

        with pytest.raises(HTTPException) as exc_info:
            proposals_service.create_proposal(
                CONNECTION,
                current_user=CONTRIBUTOR,
                payload=CountryProposalCreate(
                    slug="wakanda",
                    name_en="Wakanda",
                    name_ru="Ваканда",
                    iso2="WK",
                    iso3="WKD",
                    justification="x" * 30,
                ),
            )
        assert exc_info.value.status_code == 409
        _assert_error(exc_info, "country_slug_taken")

    def test_create_rejects_taken_iso_code(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_feature(monkeypatch)
        monkeypatch.setattr(repository, "country_slug_exists", lambda *_: False)
        monkeypatch.setattr(repository, "country_iso_exists", lambda *_a: True)

        with pytest.raises(HTTPException) as exc_info:
            proposals_service.create_proposal(
                CONNECTION,
                current_user=CONTRIBUTOR,
                payload=CountryProposalCreate(
                    slug="wakanda",
                    name_en="Wakanda",
                    name_ru="Ваканда",
                    iso2="WK",
                    iso3="WKD",
                    justification="x" * 30,
                ),
            )
        assert exc_info.value.status_code == 409
        _assert_error(exc_info, "country_iso_taken")

    def test_create_rejects_invalid_slug(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_feature(monkeypatch)
        with pytest.raises(HTTPException) as exc_info:
            proposals_service.create_proposal(
                CONNECTION,
                current_user=CONTRIBUTOR,
                payload=CountryProposalCreate(
                    slug="Not Valid",
                    name_en="Wakanda",
                    name_ru="Ваканда",
                    iso2="WK",
                    iso3="WKD",
                    justification="x" * 30,
                ),
            )
        _assert_error(exc_info, "invalid_slug")

    def test_create_succeeds_and_creates_country_shell_inactive_non_demo(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_feature(monkeypatch)
        monkeypatch.setattr(repository, "country_slug_exists", lambda *_: False)
        monkeypatch.setattr(repository, "country_iso_exists", lambda *_a: False)
        created_country = {"id": COUNTRY_ID, "slug": "wakanda"}
        monkeypatch.setattr(
            repository,
            "create_country_name_translation",
            lambda *_a, **_k: None,
        )
        monkeypatch.setattr(
            repository,
            "create_proposal_row",
            lambda *_a, **_k: {"id": PROPOSAL_ID},
        )
        monkeypatch.setattr(
            repository, "get_proposal_by_id", lambda *_a: _proposal()
        )

        captured: dict[str, Any] = {}

        def _fake_create_country_shell(
            _connection: Any, **kwargs: Any
        ) -> dict[str, Any]:
            captured.update(kwargs)
            return created_country

        monkeypatch.setattr(
            repository, "create_country_shell", _fake_create_country_shell
        )

        result = proposals_service.create_proposal(
            CONNECTION,
            current_user=CONTRIBUTOR,
            payload=CountryProposalCreate(
                slug="wakanda",
                name_en="Wakanda",
                name_ru="Ваканда",
                iso2="wk",
                iso3="wkd",
                justification="x" * 30,
            ),
        )
        assert result["slug"] == "wakanda"
        assert result["country_is_active"] is False
        assert result["country_is_demo"] is False
        assert captured["iso2"] == "WK"
        assert captured["iso3"] == "WKD"


class TestProposalCreationRace:
    def test_concurrent_slug_race_becomes_409_not_500(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from psycopg import errors as psycopg_errors

        _enable_feature(monkeypatch)
        monkeypatch.setattr(repository, "country_slug_exists", lambda *_: False)
        monkeypatch.setattr(repository, "country_iso_exists", lambda *_a: False)

        def _raise_unique_violation(*_a: Any, **_k: Any) -> Any:
            raise psycopg_errors.UniqueViolation(
                "duplicate key value violates unique constraint "
                '"countries_slug_key"'
            )

        monkeypatch.setattr(
            repository, "create_country_shell", _raise_unique_violation
        )
        monkeypatch.setattr(
            proposals_service,
            "_constraint_name",
            lambda _exc: "countries_slug_key",
        )

        with pytest.raises(HTTPException) as exc_info:
            proposals_service.create_proposal(
                CONNECTION,
                current_user=CONTRIBUTOR,
                payload=CountryProposalCreate(
                    slug="wakanda",
                    name_en="Wakanda",
                    name_ru="Ваканда",
                    iso2="WK",
                    iso3="WKD",
                    justification="x" * 30,
                ),
            )
        assert exc_info.value.status_code == 409
        _assert_error(exc_info, "country_slug_taken")

    def test_concurrent_iso_race_becomes_409_not_500(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from psycopg import errors as psycopg_errors

        _enable_feature(monkeypatch)
        monkeypatch.setattr(repository, "country_slug_exists", lambda *_: False)
        monkeypatch.setattr(repository, "country_iso_exists", lambda *_a: False)

        def _raise_unique_violation(*_a: Any, **_k: Any) -> Any:
            raise psycopg_errors.UniqueViolation(
                "duplicate key value violates unique constraint "
                '"countries_iso2_key"'
            )

        monkeypatch.setattr(
            repository, "create_country_shell", _raise_unique_violation
        )
        monkeypatch.setattr(
            proposals_service,
            "_constraint_name",
            lambda _exc: "countries_iso2_key",
        )

        with pytest.raises(HTTPException) as exc_info:
            proposals_service.create_proposal(
                CONNECTION,
                current_user=CONTRIBUTOR,
                payload=CountryProposalCreate(
                    slug="wakanda",
                    name_en="Wakanda",
                    name_ru="Ваканда",
                    iso2="WK",
                    iso3="WKD",
                    justification="x" * 30,
                ),
            )
        assert exc_info.value.status_code == 409
        _assert_error(exc_info, "country_iso_taken")


class TestProposalOwnership:
    def test_patch_requires_ownership(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_feature(monkeypatch)
        monkeypatch.setattr(
            repository, "get_proposal_for_owner", lambda *_a: None
        )

        with pytest.raises(HTTPException) as exc_info:
            proposals_service.patch_my_proposal(
                CONNECTION,
                current_user=CONTRIBUTOR,
                proposal_id=PROPOSAL_ID,
                payload=CountryProposalPatch(justification="y" * 30),
            )
        assert exc_info.value.status_code == 404

    def test_patch_locks_after_submission(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_feature(monkeypatch)
        monkeypatch.setattr(
            repository,
            "get_proposal_for_owner",
            lambda *_a: _proposal(status="review"),
        )
        monkeypatch.setattr(
            repository, "update_justification", lambda *_a, **_k: None
        )

        with pytest.raises(HTTPException) as exc_info:
            proposals_service.patch_my_proposal(
                CONNECTION,
                current_user=CONTRIBUTOR,
                proposal_id=PROPOSAL_ID,
                payload=CountryProposalPatch(justification="y" * 30),
            )
        _assert_error(exc_info, "country_proposal_not_editable")

    def test_submit_transitions_draft_to_review(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_feature(monkeypatch)
        monkeypatch.setattr(
            repository, "get_proposal_for_owner", lambda *_a: _proposal()
        )
        monkeypatch.setattr(
            repository,
            "apply_status_transition",
            lambda *_a, **_k: {"id": PROPOSAL_ID},
        )
        monkeypatch.setattr(
            repository,
            "get_proposal_by_id",
            lambda *_a: _proposal(status="review"),
        )

        result = proposals_service.submit_my_proposal(
            CONNECTION, current_user=CONTRIBUTOR, proposal_id=PROPOSAL_ID
        )
        assert result["status"] == "review"

    def test_submit_rejects_invalid_transition(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_feature(monkeypatch)
        monkeypatch.setattr(
            repository,
            "get_proposal_for_owner",
            lambda *_a: _proposal(status="published"),
        )

        with pytest.raises(HTTPException) as exc_info:
            proposals_service.submit_my_proposal(
                CONNECTION, current_user=CONTRIBUTOR, proposal_id=PROPOSAL_ID
            )
        _assert_error(exc_info, "invalid_publication_transition")


class TestContributorContentScoping:
    def test_create_source_rejects_when_not_draft(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_feature(monkeypatch)
        monkeypatch.setattr(
            repository,
            "get_proposal_for_owner",
            lambda *_a: _proposal(status="review"),
        )

        with pytest.raises(HTTPException) as exc_info:
            content_service.create_my_source(
                CONNECTION,
                current_user=CONTRIBUTOR,
                proposal_id=PROPOSAL_ID,
                payload=ContributorSourceCreate(title="A source"),
            )
        _assert_error(exc_info, "country_proposal_not_editable")

    def test_create_source_forces_draft_status_and_own_country(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_feature(monkeypatch)
        monkeypatch.setattr(
            repository, "get_proposal_for_owner", lambda *_a: _proposal()
        )
        captured: dict[str, Any] = {}

        def _fake_create_source(
            _connection: Any, payload: Any, _email: str
        ) -> Any:
            captured["payload"] = payload
            return {"id": "source-1"}

        monkeypatch.setattr(
            "app.services.admin_content.create_source", _fake_create_source
        )

        content_service.create_my_source(
            CONNECTION,
            current_user=CONTRIBUTOR,
            proposal_id=PROPOSAL_ID,
            payload=ContributorSourceCreate(title="A source"),
        )
        assert captured["payload"].status.value == "draft"
        assert captured["payload"].country_slug == "wakanda"

    def test_patch_source_rejects_cross_country_source(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_feature(monkeypatch)
        monkeypatch.setattr(
            repository, "get_proposal_for_owner", lambda *_a: _proposal()
        )
        monkeypatch.setattr(
            admin_content_repository,
            "get_source_for_admin",
            lambda *_a: {"id": "source-1", "country_id": "other-country"},
        )

        with pytest.raises(HTTPException) as exc_info:
            content_service.patch_my_source(
                CONNECTION,
                current_user=CONTRIBUTOR,
                proposal_id=PROPOSAL_ID,
                source_id="source-1",
                payload=cast(Any, MagicMock(model_dump=lambda **_: {})),
            )
        _assert_error(exc_info, "country_proposal_scope_violation")

    def test_metric_values_reject_duplicate_slug_in_one_request(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_feature(monkeypatch)
        monkeypatch.setattr(
            repository, "get_proposal_for_owner", lambda *_a: _proposal()
        )

        with pytest.raises(HTTPException) as exc_info:
            content_service.upsert_my_metric_values(
                CONNECTION,
                current_user=CONTRIBUTOR,
                proposal_id=PROPOSAL_ID,
                entries=[
                    CountryMetricValueEntry(
                        metric_slug="visa_free_count",
                        raw_value=1,
                        normalized_value=50,
                    ),
                    CountryMetricValueEntry(
                        metric_slug="visa_free_count",
                        raw_value=2,
                        normalized_value=60,
                    ),
                ],
            )
        _assert_error(exc_info, "duplicate_metric_slug")

    def test_timeline_event_requires_source_or_evidence(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_feature(monkeypatch)
        monkeypatch.setattr(
            repository, "get_proposal_for_owner", lambda *_a: _proposal()
        )
        monkeypatch.setattr(
            repository,
            "get_legal_signal_country_id",
            lambda *_a: COUNTRY_ID,
        )
        payload = MagicMock(
            legal_signal_id="signal-1",
            source_id=None,
            evidence_item_id=None,
        )

        with pytest.raises(HTTPException) as exc_info:
            content_service.create_my_timeline_event(
                CONNECTION,
                current_user=CONTRIBUTOR,
                proposal_id=PROPOSAL_ID,
                payload=payload,
            )
        _assert_error(exc_info, "timeline_event_source_required")


class TestCuratorWorkflow:
    def test_assign_curator_self_assigns(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_feature(monkeypatch)
        monkeypatch.setattr(
            repository,
            "get_proposal_by_id",
            lambda *_a: _proposal(status="review"),
        )
        monkeypatch.setattr(
            repository, "assign_curator", lambda *_a, **_k: {"id": PROPOSAL_ID}
        )

        result = curation_service.assign_curator(
            CONNECTION, current_user=EDITOR, proposal_id=PROPOSAL_ID
        )
        assert result["id"] == PROPOSAL_ID

    def test_assign_curator_rejects_when_already_assigned(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_feature(monkeypatch)
        monkeypatch.setattr(
            repository,
            "get_proposal_by_id",
            lambda *_a: _proposal(curator_user_id=OTHER_USER_ID),
        )
        monkeypatch.setattr(
            repository, "assign_curator", lambda *_a, **_k: None
        )

        with pytest.raises(HTTPException) as exc_info:
            curation_service.assign_curator(
                CONNECTION, current_user=EDITOR, proposal_id=PROPOSAL_ID
            )
        _assert_error(exc_info, "curator_already_assigned")

    def test_publish_requires_curator(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_feature(monkeypatch)
        monkeypatch.setattr(
            repository,
            "get_proposal_by_id",
            lambda *_a: _proposal(status="review", curator_user_id=None),
        )

        with pytest.raises(HTTPException) as exc_info:
            curation_service.publish_proposal(
                CONNECTION, current_user=EDITOR, proposal_id=PROPOSAL_ID
            )
        assert exc_info.value.status_code == 409
        _assert_error(exc_info, "curator_required")

    def test_publish_fails_when_onboarding_gate_is_red(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_feature(monkeypatch)
        monkeypatch.setattr(
            repository,
            "get_proposal_by_id",
            lambda *_a: _proposal(status="review", curator_user_id=EDITOR_ID),
        )
        monkeypatch.setattr(
            repository, "set_country_active", lambda *_a, **_k: None
        )
        fake_result = MagicMock(mvp_ready=False, findings=[])
        monkeypatch.setattr(
            curation_service,
            "evaluate_country_onboarding",
            lambda *_a: fake_result,
        )

        with pytest.raises(HTTPException) as exc_info:
            curation_service.publish_proposal(
                CONNECTION, current_user=EDITOR, proposal_id=PROPOSAL_ID
            )
        _assert_error(exc_info, "onboarding_gate_failed")

    def test_publish_succeeds_and_flips_country_active(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_feature(monkeypatch)
        monkeypatch.setattr(
            repository,
            "get_proposal_by_id",
            lambda *_a: _proposal(status="review", curator_user_id=EDITOR_ID),
        )
        activation_calls: list[dict[str, Any]] = []
        monkeypatch.setattr(
            repository,
            "set_country_active",
            lambda *_a, **k: activation_calls.append(k),
        )
        fake_result = MagicMock(mvp_ready=True, findings=[])
        fake_result.model_dump.return_value = {"mvp_ready": True}
        monkeypatch.setattr(
            curation_service,
            "evaluate_country_onboarding",
            lambda *_a: fake_result,
        )
        monkeypatch.setattr(
            repository, "store_readiness_snapshot", lambda *_a, **_k: None
        )
        monkeypatch.setattr(
            repository,
            "apply_status_transition",
            lambda *_a, **_k: {"id": PROPOSAL_ID},
        )

        curation_service.publish_proposal(
            CONNECTION, current_user=EDITOR, proposal_id=PROPOSAL_ID
        )
        assert activation_calls == [
            {"country_id": COUNTRY_ID, "is_active": True}
        ]

    def test_reject_requires_valid_transition(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_feature(monkeypatch)
        monkeypatch.setattr(
            repository,
            "get_proposal_by_id",
            lambda *_a: _proposal(status="published"),
        )

        with pytest.raises(HTTPException) as exc_info:
            curation_service.reject_proposal(
                CONNECTION,
                current_user=EDITOR,
                proposal_id=PROPOSAL_ID,
                reason="not ready",
            )
        _assert_error(exc_info, "invalid_publication_transition")


class TestScenarioScores:
    def _breakdown(self, **overrides: Any) -> ScenarioBreakdownEntry:
        data: dict[str, Any] = {
            "criterion": "legalization_score",
            "score": 70,
            "weight": 1 / 7,
            "explanation_en": "en",
            "explanation_ru": "ru",
            "source_ids": ["66666666-6666-6666-6666-666666666666"],
            "confidence": "medium",
        }
        data.update(overrides)
        return ScenarioBreakdownEntry(**data)

    def _full_breakdowns(self) -> list[ScenarioBreakdownEntry]:
        criteria = (
            "legalization_score",
            "long_term_status_score",
            "cost_of_living_score",
            "safety_score",
            "business_score",
            "legal_stability_score",
            "source_quality_score",
        )
        return [self._breakdown(criterion=c) for c in criteria]

    def test_rejects_incomplete_criteria_set(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_feature(monkeypatch)
        monkeypatch.setattr(
            repository, "get_proposal_by_id", lambda *_a: _proposal()
        )
        monkeypatch.setattr(
            repository, "get_scenario_id_by_slug", lambda *_a: "scenario-1"
        )

        with pytest.raises(HTTPException) as exc_info:
            scores_service.upsert_scenario_scores(
                CONNECTION,
                current_user=EDITOR,
                proposal_id=PROPOSAL_ID,
                scenario_slug="relocation_residence",
                breakdowns=self._full_breakdowns()[:6],
            )
        _assert_error(exc_info, "invalid_scenario_breakdown_criteria")

    def test_rejects_weights_not_summing_to_one(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_feature(monkeypatch)
        monkeypatch.setattr(
            repository, "get_proposal_by_id", lambda *_a: _proposal()
        )
        monkeypatch.setattr(
            repository, "get_scenario_id_by_slug", lambda *_a: "scenario-1"
        )
        breakdowns = self._full_breakdowns()
        breakdowns[0] = self._breakdown(
            criterion="legalization_score", weight=0.9
        )

        with pytest.raises(HTTPException) as exc_info:
            scores_service.upsert_scenario_scores(
                CONNECTION,
                current_user=EDITOR,
                proposal_id=PROPOSAL_ID,
                scenario_slug="relocation_residence",
                breakdowns=breakdowns,
            )
        _assert_error(exc_info, "invalid_scenario_breakdown_weights")

    def test_computes_weighted_overall_score_and_weakest_confidence(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_feature(monkeypatch)
        monkeypatch.setattr(
            repository, "get_proposal_by_id", lambda *_a: _proposal()
        )
        monkeypatch.setattr(
            repository, "get_scenario_id_by_slug", lambda *_a: "scenario-1"
        )
        stored: dict[str, Any] = {}

        def _fake_upsert_country_score(_connection: Any, **kwargs: Any) -> Any:
            stored.update(kwargs)
            return {"id": "score-1"}

        monkeypatch.setattr(
            repository, "upsert_country_score", _fake_upsert_country_score
        )
        monkeypatch.setattr(
            repository, "replace_breakdowns", lambda *_a, **_k: []
        )
        monkeypatch.setattr(
            scores_service,
            "get_active_methodology_config",
            lambda *_a: MagicMock(score_labels=MagicMock()),
        )
        monkeypatch.setattr(
            scores_service, "score_label", lambda score, _t: f"label-{score}"
        )

        breakdowns = self._full_breakdowns()
        breakdowns[-1] = self._breakdown(
            criterion="source_quality_score", confidence="low"
        )
        scores_service.upsert_scenario_scores(
            CONNECTION,
            current_user=EDITOR,
            proposal_id=PROPOSAL_ID,
            scenario_slug="relocation_residence",
            breakdowns=breakdowns,
        )
        assert stored["score"] == pytest.approx(70.0)
        assert stored["confidence"] == "low"


def test_weakest_confidence_orders_low_below_medium_below_high() -> None:
    assert helpers.weakest_confidence(["high", "low", "medium"]) == "low"
    assert helpers.weakest_confidence(["high", "medium"]) == "medium"
    assert helpers.weakest_confidence(["high"]) == "high"
