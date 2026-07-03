from app.core.auth import CurrentUser
from app.repositories import migration_board as repository
from app.schemas.migration_board import (
    CreateMigrationBoardPostRequest,
    UpdateMigrationBoardPostRequest,
)
from app.services import migration_board as service
from fastapi import HTTPException
from psycopg import Connection
import pytest
from typing import Any, cast
from unittest.mock import MagicMock


CONNECTION = cast(Connection[Any], MagicMock())
OWNER_ID = "33333333-3333-3333-3333-333333333333"
OTHER_ID = "99999999-9999-9999-9999-999999999999"
USER = CurrentUser(
    id=OWNER_ID,
    email="owner@example.local",
    display_name="Owner",
    role="user",
    status="active",
)
STRANGER = CurrentUser(
    id=OTHER_ID,
    email="stranger@example.local",
    display_name="Stranger",
    role="user",
    status="active",
)


def _post(**overrides: Any) -> dict[str, Any]:
    row = {
        "id": "22222222-2222-2222-2222-222222222222",
        "user_id": OWNER_ID,
        "author_display_name": "Author",
        "origin_country_id": None,
        "origin_country_slug": None,
        "origin_country_name": None,
        "destination_country_id": "44444444-4444-4444-4444-444444444444",
        "destination_country_slug": "uruguay",
        "destination_country_name": "Uruguay",
        "route_id": None,
        "route_slug": None,
        "route_title": None,
        "scenario_slug": None,
        "scenario_label": None,
        "persona_slug": None,
        "persona_label": None,
        "title": "Moving to Uruguay",
        "summary": "Looking for people preparing documents and housing research.",
        "target_city": None,
        "target_month": None,
        "timeline_window": "6_12_months",
        "budget_range": "undisclosed",
        "household_type": "solo",
        "migration_stage": "researching",
        "companion_goal": "info_exchange",
        "preferred_language": "en",
        "visibility": "public",
        "status": "published",
        "moderation_status": "approved",
        "risk_acknowledged": True,
        "legal_disclaimer_acknowledged": True,
        "contact_requests_enabled": True,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "submitted_at": None,
        "published_at": "2026-01-02T00:00:00Z",
        "archived_at": None,
        "rejected_at": None,
        "moderated_by": None,
        "moderated_at": None,
        "moderation_reason": None,
        "tags": ["housing"],
    }
    row.update(overrides)
    return row


def _enable_features(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(service, "is_feature_enabled_by_key", lambda *_: True)


def _create_payload(**overrides: Any) -> CreateMigrationBoardPostRequest:
    data: dict[str, Any] = {
        "destination_country_slug": "uruguay",
        "title": "Moving to Uruguay soon",
        "summary": "Looking for companions preparing documents together.",
        "risk_acknowledged": True,
        "legal_disclaimer_acknowledged": True,
    }
    data.update(overrides)
    return CreateMigrationBoardPostRequest(**data)


def _assert_error(exc: pytest.ExceptionInfo[HTTPException], code: str) -> None:
    detail = cast(dict[str, Any], exc.value.detail)
    assert detail["error"]["code"] == code


class TestVisibilityMatrix:
    def test_published_public_post_visible_to_anonymous(self) -> None:
        assert service._can_view_post(_post(), None) is True

    def test_published_public_post_visible_to_any_member(self) -> None:
        assert service._can_view_post(_post(), STRANGER) is True

    def test_members_only_post_hidden_from_anonymous(self) -> None:
        post = _post(visibility="members_only")
        assert service._can_view_post(post, None) is False

    def test_members_only_post_visible_to_any_member(self) -> None:
        post = _post(visibility="members_only")
        assert service._can_view_post(post, STRANGER) is True

    def test_private_post_hidden_from_stranger(self) -> None:
        post = _post(visibility="private")
        assert service._can_view_post(post, STRANGER) is False

    def test_private_post_visible_to_owner(self) -> None:
        post = _post(visibility="private")
        assert service._can_view_post(post, USER) is True

    def test_unapproved_post_hidden_from_stranger_even_if_public(self) -> None:
        post = _post(moderation_status="pending")
        assert service._can_view_post(post, STRANGER) is False

    def test_unapproved_post_visible_to_owner(self) -> None:
        post = _post(status="draft", moderation_status="pending")
        assert service._can_view_post(post, USER) is True

    def test_unapproved_post_hidden_from_anonymous(self) -> None:
        post = _post(status="draft", moderation_status="pending")
        assert service._can_view_post(post, None) is False

    def test_archived_post_hidden_from_stranger(self) -> None:
        post = _post(status="archived")
        assert service._can_view_post(post, STRANGER) is False


class TestContactEligibility:
    def test_receivable_when_published_approved_public_and_enabled(self) -> None:
        assert service._can_receive_contact_request(_post()) is True

    def test_not_receivable_when_contact_requests_disabled(self) -> None:
        post = _post(contact_requests_enabled=False)
        assert service._can_receive_contact_request(post) is False

    def test_not_receivable_when_visibility_private(self) -> None:
        post = _post(visibility="private")
        assert service._can_receive_contact_request(post) is False

    def test_not_receivable_when_not_published(self) -> None:
        post = _post(status="draft")
        assert service._can_receive_contact_request(post) is False

    def test_not_receivable_when_not_approved(self) -> None:
        post = _post(moderation_status="pending")
        assert service._can_receive_contact_request(post) is False

    def test_receivable_when_members_only(self) -> None:
        post = _post(visibility="members_only")
        assert service._can_receive_contact_request(post) is True


class TestPiiDetection:
    @pytest.mark.parametrize(
        "text",
        [
            "Reach me at person@example.com please",
            "Call me at +1 555 123 4567",
            "My telegram is @relocation_helper",
            "Check my blog at https://example.com/me",
            "www.example.com has more details",
        ],
    )
    def test_rejects_various_contact_detail_patterns(self, text: str) -> None:
        with pytest.raises(HTTPException) as exc_info:
            service._reject_public_pii("title", text)
        _assert_error(exc_info, "pii_not_allowed")

    def test_accepts_text_without_contact_details(self) -> None:
        service._reject_public_pii(
            "Moving to Uruguay",
            "Looking for companions who are also preparing documents this year.",
        )

    def test_short_all_caps_word_is_not_flagged_as_handle(self) -> None:
        service._reject_public_pii("Plan", "We are relocating IN JUNE next year.")


class TestEnumAndTagValidation:
    def test_validate_enum_rejects_unknown_value(self) -> None:
        with pytest.raises(HTTPException) as exc_info:
            service._validate_enum("not_a_real_value", service.ALLOWED_BUDGET_RANGES)
        _assert_error(exc_info, "invalid_enum_value")

    def test_validate_enum_allows_none(self) -> None:
        service._validate_enum(None, service.ALLOWED_BUDGET_RANGES)

    def test_validate_enum_allows_member_value(self) -> None:
        service._validate_enum("low", service.ALLOWED_BUDGET_RANGES)

    def test_validate_tags_rejects_unknown_tag(self) -> None:
        with pytest.raises(HTTPException) as exc_info:
            service._validate_tags(["housing", "not_a_real_tag"])
        _assert_error(exc_info, "invalid_tag")

    def test_validate_tags_deduplicates_preserving_order(self) -> None:
        result = service._validate_tags(["housing", "tax", "housing"])
        assert result == ["housing", "tax"]

    def test_validate_tags_empty_list_is_valid(self) -> None:
        assert service._validate_tags([]) == []


class TestCreatePost:
    def test_rejects_when_active_post_limit_reached(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository,
            "count_user_active_posts",
            lambda *_a, **_kw: service.MAX_ACTIVE_POSTS,
        )

        with pytest.raises(HTTPException) as exc_info:
            service.create_user_post(
                CONNECTION, current_user=USER, payload=_create_payload()
            )
        assert exc_info.value.status_code == 429
        _assert_error(exc_info, "active_post_limit_exceeded")

    def test_rejects_pii_before_creating(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(repository, "count_user_active_posts", lambda *_a, **_kw: 0)
        monkeypatch.setattr(
            repository,
            "get_country_by_slug",
            lambda *_a, **_kw: {"id": "44444444-4444-4444-4444-444444444444"},
        )

        with pytest.raises(HTTPException) as exc_info:
            service.create_user_post(
                CONNECTION,
                current_user=USER,
                payload=_create_payload(summary="Email me at test@example.com now"),
            )
        _assert_error(exc_info, "pii_not_allowed")

    def test_rejects_unknown_destination_country(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(repository, "count_user_active_posts", lambda *_a, **_kw: 0)
        monkeypatch.setattr(repository, "get_country_by_slug", lambda *_a, **_kw: None)

        with pytest.raises(HTTPException) as exc_info:
            service.create_user_post(
                CONNECTION, current_user=USER, payload=_create_payload()
            )
        assert exc_info.value.status_code == 404
        _assert_error(exc_info, "destination_country_not_found")

    def test_rejects_route_from_different_country(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(repository, "count_user_active_posts", lambda *_a, **_kw: 0)
        monkeypatch.setattr(
            repository,
            "get_country_by_slug",
            lambda *_a, **_kw: {"id": "44444444-4444-4444-4444-444444444444"},
        )
        monkeypatch.setattr(
            repository,
            "get_route_for_validation",
            lambda *_a, **_kw: {"country_id": "other-country-id"},
        )

        with pytest.raises(HTTPException) as exc_info:
            service.create_user_post(
                CONNECTION,
                current_user=USER,
                payload=_create_payload(
                    route_id="66666666-6666-6666-6666-666666666666"
                ),
            )
        assert exc_info.value.status_code == 422
        _assert_error(exc_info, "route_destination_mismatch")

    def test_creates_post_successfully_with_valid_payload(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(repository, "count_user_active_posts", lambda *_a, **_kw: 0)
        monkeypatch.setattr(
            repository,
            "get_country_by_slug",
            lambda *_a, **_kw: {"id": "44444444-4444-4444-4444-444444444444"},
        )
        monkeypatch.setattr(repository, "create_post", lambda *_a, **_kw: _post())
        monkeypatch.setattr(service, "_audit", lambda *_a, **_kw: None)
        monkeypatch.setattr(service, "_track_event", lambda *_a, **_kw: None)

        result = service.create_user_post(
            CONNECTION, current_user=USER, payload=_create_payload()
        )
        assert result["status"] == "published"


class TestUpdatePost:
    def test_rejects_update_on_deleted_style_status(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository,
            "get_post_for_owner",
            lambda *_a, **_kw: _post(status="matched"),
        )

        with pytest.raises(HTTPException) as exc_info:
            service.update_user_post(
                CONNECTION,
                current_user=USER,
                post_id="22222222-2222-2222-2222-222222222222",
                payload=UpdateMigrationBoardPostRequest(),
            )
        assert exc_info.value.status_code == 409
        _assert_error(exc_info, "invalid_post_status")

    def test_significant_edit_on_published_post_resets_to_review(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_post_for_owner", lambda *_a, **_kw: _post()
        )
        captured: dict[str, Any] = {}

        def fake_update(_conn: Any, **kwargs: Any) -> dict[str, Any]:
            captured.update(kwargs)
            return _post(status="review")

        monkeypatch.setattr(repository, "update_post", fake_update)
        monkeypatch.setattr(service, "_audit", lambda *_a, **_kw: None)

        service.update_user_post(
            CONNECTION,
            current_user=USER,
            post_id="22222222-2222-2222-2222-222222222222",
            payload=UpdateMigrationBoardPostRequest(title="A brand new title here"),
        )
        assert captured["reset_to_review"] is True

    def test_non_significant_edit_on_published_post_does_not_reset(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_post_for_owner", lambda *_a, **_kw: _post()
        )
        captured: dict[str, Any] = {}

        def fake_update(_conn: Any, **kwargs: Any) -> dict[str, Any]:
            captured.update(kwargs)
            return _post()

        monkeypatch.setattr(repository, "update_post", fake_update)
        monkeypatch.setattr(service, "_audit", lambda *_a, **_kw: None)

        service.update_user_post(
            CONNECTION,
            current_user=USER,
            post_id="22222222-2222-2222-2222-222222222222",
            payload=UpdateMigrationBoardPostRequest(
                contact_requests_enabled=False, tags=["tax"]
            ),
        )
        assert captured["reset_to_review"] is False

    def test_update_returns_404_when_repository_finds_nothing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_post_for_owner", lambda *_a, **_kw: _post(status="draft")
        )
        monkeypatch.setattr(repository, "update_post", lambda *_a, **_kw: None)

        with pytest.raises(HTTPException) as exc_info:
            service.update_user_post(
                CONNECTION,
                current_user=USER,
                post_id="22222222-2222-2222-2222-222222222222",
                payload=UpdateMigrationBoardPostRequest(),
            )
        assert exc_info.value.status_code == 404


class TestSubmitAndAcknowledgements:
    def test_submit_requires_risk_acknowledged(self) -> None:
        with pytest.raises(HTTPException) as exc_info:
            service._require_submit_ready(_post(risk_acknowledged=False))
        _assert_error(exc_info, "acknowledgements_required")

    def test_submit_requires_legal_disclaimer_acknowledged(self) -> None:
        with pytest.raises(HTTPException) as exc_info:
            service._require_submit_ready(_post(legal_disclaimer_acknowledged=False))
        _assert_error(exc_info, "acknowledgements_required")

    def test_submit_ready_passes_with_both_acknowledgements(self) -> None:
        service._require_submit_ready(_post())

    def test_submit_still_rejects_pii_even_if_acknowledged(self) -> None:
        with pytest.raises(HTTPException) as exc_info:
            service._require_submit_ready(
                _post(summary="Email test@example.com for details")
            )
        _assert_error(exc_info, "pii_not_allowed")

    def test_submit_invalid_transition_raises_409(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_post_for_owner", lambda *_a, **_kw: _post(status="draft")
        )
        monkeypatch.setattr(repository, "submit_post_for_review", lambda *_a: None)

        with pytest.raises(HTTPException) as exc_info:
            service.submit_user_post(
                CONNECTION,
                current_user=USER,
                post_id="22222222-2222-2222-2222-222222222222",
            )
        assert exc_info.value.status_code == 409
        _assert_error(exc_info, "invalid_status_transition")


class TestArchive:
    def test_archive_invalid_transition_raises_409(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_post_for_owner", lambda *_a, **_kw: _post()
        )
        monkeypatch.setattr(repository, "archive_post", lambda *_a, **_kw: None)

        with pytest.raises(HTTPException) as exc_info:
            service.archive_user_post(
                CONNECTION,
                current_user=USER,
                post_id="22222222-2222-2222-2222-222222222222",
            )
        assert exc_info.value.status_code == 409


class TestModeration:
    def test_approve_requires_acknowledgements(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository,
            "get_post_by_id",
            lambda *_a, **_kw: _post(risk_acknowledged=False),
        )

        with pytest.raises(HTTPException) as exc_info:
            service.approve_post(
                CONNECTION,
                current_user=USER,
                post_id="22222222-2222-2222-2222-222222222222",
            )
        _assert_error(exc_info, "acknowledgements_required")

    def test_approve_missing_post_raises_404(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(repository, "get_post_by_id", lambda *_a, **_kw: None)

        with pytest.raises(HTTPException) as exc_info:
            service.approve_post(CONNECTION, current_user=USER, post_id="missing")
        assert exc_info.value.status_code == 404

    def test_reject_invalid_transition_raises_409(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(repository, "get_post_by_id", lambda *_a, **_kw: _post())
        monkeypatch.setattr(repository, "reject_post", lambda *_a, **_kw: None)

        with pytest.raises(HTTPException) as exc_info:
            service.reject_post(
                CONNECTION,
                current_user=USER,
                post_id="22222222-2222-2222-2222-222222222222",
                reason="not relevant",
            )
        assert exc_info.value.status_code == 409

    def test_hide_missing_post_raises_404(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(repository, "get_post_by_id", lambda *_a, **_kw: None)

        with pytest.raises(HTTPException) as exc_info:
            service.hide_post(
                CONNECTION, current_user=USER, post_id="missing", reason="spam"
            )
        assert exc_info.value.status_code == 404


class TestContactRequestLifecycle:
    def test_rejects_when_post_cannot_receive_contact(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository,
            "get_post_by_id",
            lambda *_a, **_kw: _post(contact_requests_enabled=False),
        )

        with pytest.raises(HTTPException) as exc_info:
            service.create_contact_request(
                CONNECTION,
                current_user=STRANGER,
                post_id="22222222-2222-2222-2222-222222222222",
                message="Would love to compare notes on relocating.",
            )
        assert exc_info.value.status_code == 404

    def test_rejects_duplicate_pending_request(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(repository, "get_post_by_id", lambda *_a, **_kw: _post())
        monkeypatch.setattr(repository, "is_user_blocked", lambda *_a, **_kw: False)
        monkeypatch.setattr(
            repository, "pending_contact_request_exists", lambda *_a, **_kw: True
        )

        with pytest.raises(HTTPException) as exc_info:
            service.create_contact_request(
                CONNECTION,
                current_user=STRANGER,
                post_id="22222222-2222-2222-2222-222222222222",
                message="Would love to compare notes on relocating.",
            )
        assert exc_info.value.status_code == 409
        _assert_error(exc_info, "duplicate_pending_contact_request")

    def test_rejects_when_daily_limit_reached(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(repository, "get_post_by_id", lambda *_a, **_kw: _post())
        monkeypatch.setattr(repository, "is_user_blocked", lambda *_a, **_kw: False)
        monkeypatch.setattr(
            repository, "pending_contact_request_exists", lambda *_a, **_kw: False
        )
        monkeypatch.setattr(
            repository,
            "count_contact_requests_created_since",
            lambda *_a, **_kw: service.MAX_CONTACT_REQUESTS_PER_DAY,
        )

        with pytest.raises(HTTPException) as exc_info:
            service.create_contact_request(
                CONNECTION,
                current_user=STRANGER,
                post_id="22222222-2222-2222-2222-222222222222",
                message="Would love to compare notes on relocating.",
            )
        assert exc_info.value.status_code == 429
        _assert_error(exc_info, "contact_request_limit_exceeded")

    def test_accept_rejects_when_current_user_is_not_recipient(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository,
            "get_contact_request_by_id",
            lambda *_a, **_kw: {
                "id": "req-1",
                "from_user_id": OWNER_ID,
                "to_user_id": OTHER_ID,
            },
        )

        with pytest.raises(HTTPException) as exc_info:
            service.accept_contact_request(
                CONNECTION,
                current_user=USER,
                request_id="req-1",
                response_note=None,
            )
        assert exc_info.value.status_code == 404
        _assert_error(exc_info, "contact_request_not_found")

    def test_cancel_rejects_when_current_user_is_not_sender(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository,
            "get_contact_request_by_id",
            lambda *_a, **_kw: {
                "id": "req-1",
                "from_user_id": OWNER_ID,
                "to_user_id": OTHER_ID,
            },
        )

        with pytest.raises(HTTPException) as exc_info:
            service.cancel_contact_request(
                CONNECTION, current_user=STRANGER, request_id="req-1"
            )
        assert exc_info.value.status_code == 404

    def test_accept_succeeds_for_recipient(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository,
            "get_contact_request_by_id",
            lambda *_a, **_kw: {
                "id": "req-1",
                "from_user_id": OTHER_ID,
                "to_user_id": OWNER_ID,
            },
        )
        monkeypatch.setattr(
            repository,
            "update_contact_request_status",
            lambda *_a, **_kw: {
                "id": "req-1",
                "post_id": "22222222-2222-2222-2222-222222222222",
                "post_title": "Moving to Uruguay",
                "from_user_display_name": "Stranger",
                "to_user_display_name": "Owner",
                "message": "hi",
                "status": "accepted",
                "created_at": "2026-01-01T00:00:00Z",
                "responded_at": "2026-01-02T00:00:00Z",
                "cancelled_at": None,
                "response_note": None,
            },
        )
        monkeypatch.setattr(service, "_audit", lambda *_a, **_kw: None)

        result = service.accept_contact_request(
            CONNECTION, current_user=USER, request_id="req-1", response_note=None
        )
        assert result["status"] == "accepted"

    def test_invalid_status_transition_raises_409(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository,
            "get_contact_request_by_id",
            lambda *_a, **_kw: {
                "id": "req-1",
                "from_user_id": OTHER_ID,
                "to_user_id": OWNER_ID,
            },
        )
        monkeypatch.setattr(
            repository, "update_contact_request_status", lambda *_a, **_kw: None
        )

        with pytest.raises(HTTPException) as exc_info:
            service.accept_contact_request(
                CONNECTION, current_user=USER, request_id="req-1", response_note=None
            )
        assert exc_info.value.status_code == 409


class TestReports:
    def test_rejects_invalid_reason(self) -> None:
        with pytest.raises(HTTPException) as exc_info:
            service._validate_report("not_a_reason", None)
        _assert_error(exc_info, "invalid_report_reason")

    def test_rejects_overly_long_details(self) -> None:
        with pytest.raises(HTTPException) as exc_info:
            service._validate_report("spam", "x" * 1001)
        _assert_error(exc_info, "report_details_too_long")

    def test_accepts_valid_reason_and_details(self) -> None:
        service._validate_report("spam", "short note")

    def test_report_post_missing_post_raises_404(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(repository, "get_post_by_id", lambda *_a, **_kw: None)

        with pytest.raises(HTTPException) as exc_info:
            service.report_post(
                CONNECTION,
                current_user=STRANGER,
                post_id="missing",
                reason="spam",
                details=None,
            )
        assert exc_info.value.status_code == 404

    def test_report_contact_request_rejects_uninvolved_user(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository,
            "get_contact_request_by_id",
            lambda *_a, **_kw: {
                "id": "req-1",
                "from_user_id": OWNER_ID,
                "to_user_id": OTHER_ID,
            },
        )
        third_party = CurrentUser(
            id="55555555-5555-5555-5555-555555555555",
            email="third@example.local",
            display_name="Third",
            role="user",
            status="active",
        )

        with pytest.raises(HTTPException) as exc_info:
            service.report_contact_request(
                CONNECTION,
                current_user=third_party,
                request_id="req-1",
                reason="spam",
                details=None,
            )
        assert exc_info.value.status_code == 404

    def test_daily_report_limit_enforced(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(repository, "get_post_by_id", lambda *_a, **_kw: _post())
        monkeypatch.setattr(
            repository,
            "count_reports_created_today",
            lambda *_a, **_kw: service.MAX_REPORTS_PER_DAY,
        )

        with pytest.raises(HTTPException) as exc_info:
            service.report_post(
                CONNECTION,
                current_user=STRANGER,
                post_id="22222222-2222-2222-2222-222222222222",
                reason="spam",
                details=None,
            )
        assert exc_info.value.status_code == 429
        _assert_error(exc_info, "report_limit_exceeded")

    def test_duplicate_pending_report_rejected(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(repository, "get_post_by_id", lambda *_a, **_kw: _post())
        monkeypatch.setattr(
            repository, "count_reports_created_today", lambda *_a, **_kw: 0
        )
        monkeypatch.setattr(
            repository, "existing_pending_report_exists", lambda *_a, **_kw: True
        )

        with pytest.raises(HTTPException) as exc_info:
            service.report_post(
                CONNECTION,
                current_user=STRANGER,
                post_id="22222222-2222-2222-2222-222222222222",
                reason="spam",
                details=None,
            )
        assert exc_info.value.status_code == 409
        _assert_error(exc_info, "duplicate_pending_report")

    def test_resolve_report_hides_related_post_when_requested(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository,
            "get_report_by_id",
            lambda *_a, **_kw: {"id": "report-1", "status": "pending"},
        )
        monkeypatch.setattr(
            repository,
            "update_report_status",
            lambda *_a, **_kw: {
                "id": "report-1",
                "post_id": "22222222-2222-2222-2222-222222222222",
                "status": "resolved",
                "reason": "spam",
                "created_at": "2026-01-01T00:00:00Z",
                "reviewed_at": "2026-01-02T00:00:00Z",
                "resolution_note": "removed",
            },
        )
        hidden: dict[str, Any] = {}
        monkeypatch.setattr(
            repository, "hide_post", lambda *_a, **kwargs: hidden.update(kwargs)
        )
        monkeypatch.setattr(service, "_audit", lambda *_a, **_kw: None)

        service.resolve_report(
            CONNECTION,
            current_user=USER,
            report_id="report-1",
            resolution_note="removed",
            hide_related_post=True,
        )
        assert hidden["post_id"] == "22222222-2222-2222-2222-222222222222"

    def test_dismiss_report_never_hides_post(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository,
            "get_report_by_id",
            lambda *_a, **_kw: {"id": "report-1", "status": "pending"},
        )
        monkeypatch.setattr(
            repository,
            "update_report_status",
            lambda *_a, **_kw: {
                "id": "report-1",
                "post_id": "22222222-2222-2222-2222-222222222222",
                "status": "dismissed",
                "reason": "spam",
                "created_at": "2026-01-01T00:00:00Z",
                "reviewed_at": "2026-01-02T00:00:00Z",
                "resolution_note": None,
            },
        )
        hide_called = False

        def fake_hide(*_a: Any, **_kw: Any) -> None:
            nonlocal hide_called
            hide_called = True

        monkeypatch.setattr(repository, "hide_post", fake_hide)
        monkeypatch.setattr(service, "_audit", lambda *_a, **_kw: None)

        service.dismiss_report(
            CONNECTION, current_user=USER, report_id="report-1", resolution_note=None
        )
        assert hide_called is False


class TestBlocking:
    def test_self_block_not_allowed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _enable_features(monkeypatch)
        with pytest.raises(HTTPException) as exc_info:
            service.block_user(
                CONNECTION, current_user=USER, blocked_user_id=USER.id, reason=None
            )
        _assert_error(exc_info, "self_block_not_allowed")

    def test_block_unknown_user_raises_404(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(repository, "user_exists", lambda *_a, **_kw: False)

        with pytest.raises(HTTPException) as exc_info:
            service.block_user(
                CONNECTION, current_user=USER, blocked_user_id=OTHER_ID, reason=None
            )
        assert exc_info.value.status_code == 404


class TestCompanionMatching:
    def test_no_eligible_source_post_raises_404(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(repository, "list_user_posts", lambda *_a, **_kw: [])

        with pytest.raises(HTTPException) as exc_info:
            service.list_companion_matches(
                CONNECTION, current_user=USER, post_id=None, limit=10
            )
        _assert_error(exc_info, "source_post_not_found")

    def test_archived_only_posts_are_not_eligible_sources(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository,
            "list_user_posts",
            lambda *_a, **_kw: [_post(status="archived")],
        )

        with pytest.raises(HTTPException) as exc_info:
            service.list_companion_matches(
                CONNECTION, current_user=USER, post_id=None, limit=10
            )
        _assert_error(exc_info, "source_post_not_found")

    def test_match_reasons_accumulate_for_multiple_shared_attributes(self) -> None:
        source = _post(
            route_id="route-1",
            timeline_window="0_3_months",
            scenario_slug="residence",
            persona_slug="family",
            companion_goal="housing_search",
        )
        candidate = _post(
            route_id="route-1",
            timeline_window="0_3_months",
            scenario_slug="residence",
            persona_slug="family",
            companion_goal="housing_search",
        )
        reasons = service._match_reasons(source, candidate)
        assert reasons == [
            "same_destination",
            "same_route",
            "similar_timeline",
            "same_scenario",
            "same_persona",
            "same_goal",
        ]

    def test_match_reasons_minimal_when_nothing_shared(self) -> None:
        source = _post(
            route_id="route-1",
            timeline_window="0_3_months",
            companion_goal="housing_search",
        )
        candidate = _post(
            route_id="route-2",
            timeline_window="12_plus_months",
            companion_goal="study_group",
        )
        reasons = service._match_reasons(source, candidate)
        assert reasons == ["same_destination"]


class TestMiscHelpers:
    def test_is_significant_edit_true_for_title_change(self) -> None:
        payload = UpdateMigrationBoardPostRequest(title="A new significant title")
        assert service._is_significant_edit(payload) is True

    def test_is_significant_edit_false_for_visibility_only_toggle(self) -> None:
        payload = UpdateMigrationBoardPostRequest(contact_requests_enabled=False)
        assert service._is_significant_edit(payload) is False

    def test_is_significant_edit_false_for_empty_payload(self) -> None:
        payload = UpdateMigrationBoardPostRequest()
        assert service._is_significant_edit(payload) is False

    def test_diff_for_update_reports_no_field_changes_as_updated_flag(self) -> None:
        before = _post()
        after = _post()
        assert service._diff_for_update(before, after) == {"updated": {"new": True}}

    def test_diff_for_update_reports_status_change(self) -> None:
        before = _post(status="review")
        after = _post(status="published")
        diff = service._diff_for_update(before, after)
        assert diff["status"] == {"old": "review", "new": "published"}

    def test_total_returns_zero_for_empty_rows(self) -> None:
        assert service._total([]) == 0

    def test_total_reads_window_function_count(self) -> None:
        rows = [{"total_count": 42}, {"total_count": 42}]
        assert service._total(rows) == 42

    def test_total_falls_back_to_row_count_without_window_column(self) -> None:
        rows = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
        assert service._total(rows) == 3


class TestFeatureFlagGating:
    def test_ensure_feature_enabled_raises_403_when_disabled(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(service, "is_feature_enabled_by_key", lambda *_: False)

        with pytest.raises(HTTPException) as exc_info:
            service.ensure_feature_enabled(CONNECTION, service.BOARD_FEATURE_KEY)
        assert exc_info.value.status_code == 403
        _assert_error(exc_info, "feature_disabled")

    def test_matching_requires_both_board_and_matching_flags(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def flag_side_effect(_conn: Any, key: str) -> bool:
            return key != service.MATCHING_FEATURE_KEY

        monkeypatch.setattr(service, "is_feature_enabled_by_key", flag_side_effect)

        with pytest.raises(HTTPException) as exc_info:
            service.list_companion_matches(
                CONNECTION, current_user=USER, post_id=None, limit=10
            )
        detail = cast(dict[str, Any], exc_info.value.detail)
        assert detail["error"]["details"]["feature_key"] == service.MATCHING_FEATURE_KEY


class TestReadOnlyWrappers:
    def test_list_public_posts_wraps_rows_and_pagination(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        captured: dict[str, Any] = {}

        def fake_list(_conn: Any, **kwargs: Any) -> list[dict[str, Any]]:
            captured.update(kwargs)
            return [_post(), _post(id="other-id")]

        monkeypatch.setattr(repository, "list_public_posts", fake_list)
        monkeypatch.setattr(service, "_track_event", lambda *_a, **_kw: None)

        result = service.list_public_posts(
            CONNECTION,
            current_user=None,
            filters={"destination_country_slug": "uruguay"},
            limit=20,
            offset=0,
        )
        assert captured["include_members_only"] is False
        assert captured["include_private_for_user_id"] is None
        assert result["limit"] == 20
        assert len(result["items"]) == 2

    def test_list_public_posts_includes_members_only_for_logged_in_user(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        captured: dict[str, Any] = {}

        def fake_list(_conn: Any, **kwargs: Any) -> list[dict[str, Any]]:
            captured.update(kwargs)
            return []

        monkeypatch.setattr(repository, "list_public_posts", fake_list)
        monkeypatch.setattr(service, "_track_event", lambda *_a, **_kw: None)

        service.list_public_posts(
            CONNECTION, current_user=USER, filters={}, limit=20, offset=0
        )
        assert captured["include_members_only"] is True
        assert captured["include_private_for_user_id"] == USER.id

    def test_get_public_post_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(repository, "get_post_by_id", lambda *_a, **_kw: _post())
        monkeypatch.setattr(service, "_track_event", lambda *_a, **_kw: None)

        result = service.get_public_post(
            CONNECTION,
            post_id="22222222-2222-2222-2222-222222222222",
            current_user=None,
        )
        assert result["title"] == "Moving to Uruguay"

    def test_get_public_post_not_found_when_not_viewable(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_post_by_id", lambda *_a, **_kw: _post(visibility="private")
        )

        with pytest.raises(HTTPException) as exc_info:
            service.get_public_post(
                CONNECTION,
                post_id="22222222-2222-2222-2222-222222222222",
                current_user=None,
            )
        assert exc_info.value.status_code == 404

    def test_list_my_posts_returns_wrapped_items(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "list_user_posts", lambda *_a, **_kw: [_post(), _post()]
        )

        result = service.list_my_posts(CONNECTION, USER)
        assert result["total"] == 2

    def test_get_my_post_delegates_to_owner_lookup(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_post_for_owner", lambda *_a, **_kw: _post()
        )

        result = service.get_my_post(
            CONNECTION,
            current_user=USER,
            post_id="22222222-2222-2222-2222-222222222222",
        )
        assert result["status"] == "published"

    def test_list_incoming_and_outgoing_requests(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        request_row = {
            "id": "req-1",
            "post_id": "22222222-2222-2222-2222-222222222222",
            "post_title": "Moving to Uruguay",
            "from_user_display_name": "Stranger",
            "to_user_display_name": "Owner",
            "message": "hi",
            "status": "pending",
            "created_at": "2026-01-01T00:00:00Z",
            "responded_at": None,
            "cancelled_at": None,
            "response_note": None,
        }
        monkeypatch.setattr(
            repository,
            "list_incoming_contact_requests",
            lambda *_a, **_kw: [request_row],
        )
        monkeypatch.setattr(
            repository, "list_outgoing_contact_requests", lambda *_a, **_kw: []
        )

        incoming = service.list_incoming_requests(CONNECTION, USER)
        outgoing = service.list_outgoing_requests(CONNECTION, USER)
        assert incoming["total"] == 1
        assert outgoing["total"] == 0

    def test_list_blocked_users(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository,
            "list_blocked_users",
            lambda *_a, **_kw: [{"blocked_user_id": OTHER_ID}],
        )

        result = service.list_blocked_users(CONNECTION, USER)
        assert result["total"] == 1

    def test_unblock_user_writes_audit_entry(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(repository, "unblock_user", lambda *_a, **_kw: None)
        audit_calls: list[tuple[Any, ...]] = []
        monkeypatch.setattr(service, "_audit", lambda *args: audit_calls.append(args))

        service.unblock_user(CONNECTION, current_user=USER, blocked_user_id=OTHER_ID)

        assert len(audit_calls) == 1
        assert audit_calls[0][2] == "user_unblocked"

    def test_list_posts_for_moderation_requires_moderation_flag(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def flag_side_effect(_conn: Any, key: str) -> bool:
            return key != service.MODERATION_FEATURE_KEY

        monkeypatch.setattr(service, "is_feature_enabled_by_key", flag_side_effect)

        with pytest.raises(HTTPException) as exc_info:
            service.list_posts_for_moderation(
                CONNECTION, status="review", limit=20, offset=0
            )
        detail = cast(dict[str, Any], exc_info.value.detail)
        assert (
            detail["error"]["details"]["feature_key"] == service.MODERATION_FEATURE_KEY
        )

    def test_get_post_for_moderation_not_found(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(repository, "get_post_by_id", lambda *_a, **_kw: None)

        with pytest.raises(HTTPException) as exc_info:
            service.get_post_for_moderation(CONNECTION, "missing")
        assert exc_info.value.status_code == 404

    def test_list_reports_for_moderation_returns_total(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository,
            "list_reports_for_moderation",
            lambda *_a, **_kw: [
                {
                    "id": "report-1",
                    "post_id": "22222222-2222-2222-2222-222222222222",
                    "contact_request_id": None,
                    "reason": "spam",
                    "details": None,
                    "status": "pending",
                    "created_at": "2026-01-01T00:00:00Z",
                    "reviewed_at": None,
                    "resolution_note": None,
                }
            ],
        )

        result = service.list_reports_for_moderation(
            CONNECTION, status="pending", limit=20, offset=0
        )
        assert result["total"] == 1
