"""Author metrics service: lifecycle, PII/methodology/coverage gates, values, subscriptions, forks, reputation."""

import pytest
from app.core.auth import CurrentUser
from app.repositories import author_metrics as repository
from app.schemas.author_metrics import (
    AuthorMetricValueItem,
    CreateAuthorMetricRequest,
    UpdateAuthorMetricRequest,
)
from app.services import (
    author_metrics as service,
    feature_flags as feature_flags_service,
)
from app.services.author_metrics import (
    helpers,
    reputation as reputation_service,
)
from datetime import UTC, datetime
from fastapi import HTTPException
from psycopg import Connection
from typing import Any, cast
from unittest.mock import MagicMock


CONNECTION = cast(Connection[Any], MagicMock())
AUTHOR_ID = "33333333-3333-3333-3333-333333333333"
MODERATOR_ID = "55555555-5555-5555-5555-555555555555"
AUTHOR = CurrentUser(
    id=AUTHOR_ID,
    email="author@example.local",
    display_name="Author",
    role="user",
    status="active",
)
MODERATOR = CurrentUser(
    id=MODERATOR_ID,
    email="moderator@example.local",
    display_name="Moderator",
    role="moderator",
    status="active",
)


def _definition(**overrides: Any) -> dict[str, Any]:
    row = {
        "id": "22222222-2222-2222-2222-222222222222",
        "author_user_id": AUTHOR_ID,
        "author_display_name": "Author",
        "slug": "cost-of-living-index",
        "name_en": "Cost of Living Index",
        "name_ru": "Индекс стоимости жизни",
        "methodology_en": "x" * 80,
        "methodology_ru": "y" * 80,
        "polarity": "lower_is_better",
        "scale_min": 0,
        "scale_max": 100,
        "license": "platform",
        "status": "draft",
        "visibility": "private",
        "forked_from_id": None,
        "version": 1,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "submitted_at": None,
        "published_at": None,
        "archived_at": None,
        "rejected_at": None,
        "moderated_by": None,
        "moderated_at": None,
        "moderation_reason": None,
    }
    row.update(overrides)
    return row


def _enable_features(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        feature_flags_service, "is_feature_enabled_by_key", lambda *_: True
    )
    monkeypatch.setattr(helpers, "min_methodology_length", lambda *_: 120)
    monkeypatch.setattr(helpers, "min_country_coverage", lambda *_: 5)


def _create_payload(**overrides: Any) -> CreateAuthorMetricRequest:
    data: dict[str, Any] = {
        "slug": "cost-of-living-index",
        "name_en": "Cost of Living Index",
        "name_ru": "Индекс стоимости жизни",
    }
    data.update(overrides)
    return CreateAuthorMetricRequest(**data)


def _assert_error(exc: pytest.ExceptionInfo[HTTPException], code: str) -> None:
    detail = cast(dict[str, Any], exc.value.detail)
    assert detail["error"]["code"] == code


class TestDefinitionLifecycle:
    def test_create_rejects_duplicate_slug(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository,
            "get_definition_by_author_slug",
            lambda *_a: _definition(),
        )

        with pytest.raises(HTTPException) as exc_info:
            service.create_my_definition(
                CONNECTION, current_user=AUTHOR, payload=_create_payload()
            )
        assert exc_info.value.status_code == 409
        _assert_error(exc_info, "author_metric_slug_taken")

    def test_create_rejects_pii_in_name(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_definition_by_author_slug", lambda *_a: None
        )

        with pytest.raises(HTTPException) as exc_info:
            service.create_my_definition(
                CONNECTION,
                current_user=AUTHOR,
                payload=_create_payload(
                    name_en="Contact me at person@example.com"
                ),
            )
        _assert_error(exc_info, "pii_not_allowed")

    def test_create_rejects_invalid_scale(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_definition_by_author_slug", lambda *_a: None
        )

        with pytest.raises(HTTPException) as exc_info:
            service.create_my_definition(
                CONNECTION,
                current_user=AUTHOR,
                payload=_create_payload(scale_min=100, scale_max=0),
            )
        _assert_error(exc_info, "invalid_scale")

    def test_create_succeeds_with_valid_payload(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_definition_by_author_slug", lambda *_a: None
        )
        monkeypatch.setattr(
            repository, "create_definition", lambda *_a, **_kw: _definition()
        )
        monkeypatch.setattr(helpers, "_audit", lambda *_a, **_kw: None)

        result = service.create_my_definition(
            CONNECTION, current_user=AUTHOR, payload=_create_payload()
        )
        assert result["status"] == "draft"
        assert result["author"]["user_id"] == AUTHOR_ID

    def test_concurrent_slug_race_becomes_409_not_500(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from psycopg import errors as psycopg_errors

        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_definition_by_author_slug", lambda *_a: None
        )

        def _raise_unique_violation(*_a: Any, **_k: Any) -> Any:
            raise psycopg_errors.UniqueViolation(
                "duplicate key value violates unique constraint "
                '"uq_author_metric_definitions_author_slug"'
            )

        monkeypatch.setattr(
            repository, "create_definition", _raise_unique_violation
        )

        with pytest.raises(HTTPException) as exc_info:
            service.create_my_definition(
                CONNECTION, current_user=AUTHOR, payload=_create_payload()
            )
        assert exc_info.value.status_code == 409
        _assert_error(exc_info, "author_metric_slug_taken")

    def test_submit_requires_methodology_length(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository,
            "get_definition_for_author",
            lambda *_a: _definition(
                methodology_en="short", methodology_ru="short"
            ),
        )

        with pytest.raises(HTTPException) as exc_info:
            service.submit_my_definition(
                CONNECTION, current_user=AUTHOR, definition_id="d-1"
            )
        assert exc_info.value.status_code == 422
        _assert_error(exc_info, "methodology_too_short")

    def test_submit_rejects_pii_in_methodology(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository,
            "get_definition_for_author",
            lambda *_a: _definition(
                methodology_en="Email me at person@example.com " + "x" * 100
            ),
        )

        with pytest.raises(HTTPException) as exc_info:
            service.submit_my_definition(
                CONNECTION, current_user=AUTHOR, definition_id="d-1"
            )
        _assert_error(exc_info, "pii_not_allowed")

    def test_submit_succeeds_when_ready(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_definition_for_author", lambda *_a: _definition()
        )
        monkeypatch.setattr(
            repository,
            "submit_definition_for_review",
            lambda *_a: _definition(status="review"),
        )
        monkeypatch.setattr(helpers, "_audit", lambda *_a, **_kw: None)

        result = service.submit_my_definition(
            CONNECTION, current_user=AUTHOR, definition_id="d-1"
        )
        assert result["status"] == "review"

    def test_update_locks_license_once_submitted(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository,
            "get_definition_for_author",
            lambda *_a: _definition(status="review"),
        )

        with pytest.raises(HTTPException) as exc_info:
            service.update_my_definition(
                CONNECTION,
                current_user=AUTHOR,
                definition_id="d-1",
                payload=UpdateAuthorMetricRequest(license="cc_by_sa"),
            )
        assert exc_info.value.status_code == 409
        _assert_error(exc_info, "license_locked")

    def test_update_allows_license_change_while_draft(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_definition_for_author", lambda *_a: _definition()
        )
        monkeypatch.setattr(
            repository,
            "update_definition",
            lambda *_a, **_kw: _definition(license="cc_by_sa"),
        )
        monkeypatch.setattr(helpers, "_audit", lambda *_a, **_kw: None)

        result = service.update_my_definition(
            CONNECTION,
            current_user=AUTHOR,
            definition_id="d-1",
            payload=UpdateAuthorMetricRequest(license="cc_by_sa"),
        )
        assert result["license"] == "cc_by_sa"

    def test_archive_invalid_transition_raises_409(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_definition_for_author", lambda *_a: _definition()
        )
        monkeypatch.setattr(repository, "archive_definition", lambda *_a: None)

        with pytest.raises(HTTPException) as exc_info:
            service.archive_my_definition(
                CONNECTION, current_user=AUTHOR, definition_id="d-1"
            )
        assert exc_info.value.status_code == 409
        _assert_error(exc_info, "invalid_status_transition")


class TestModeration:
    def test_approve_requires_country_coverage(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository,
            "get_definition_by_id",
            lambda *_a: _definition(status="review"),
        )
        monkeypatch.setattr(
            repository, "count_countries_with_values", lambda *_a: 1
        )

        with pytest.raises(HTTPException) as exc_info:
            service.approve_definition(
                CONNECTION, current_user=MODERATOR, definition_id="d-1"
            )
        assert exc_info.value.status_code == 422
        _assert_error(exc_info, "insufficient_country_coverage")

    def test_approve_rejects_moderator_who_is_the_author(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository,
            "get_definition_by_id",
            lambda *_a: _definition(status="review"),
        )

        author_as_moderator = CurrentUser(
            id=AUTHOR_ID,
            email="author@example.local",
            display_name="Author",
            role="moderator",
            status="active",
        )
        with pytest.raises(HTTPException) as exc_info:
            service.approve_definition(
                CONNECTION,
                current_user=author_as_moderator,
                definition_id="d-1",
            )
        assert exc_info.value.status_code == 403
        _assert_error(exc_info, "moderation_conflict_of_interest")

    def test_approve_succeeds_with_sufficient_coverage(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository,
            "get_definition_by_id",
            lambda *_a: _definition(status="review"),
        )
        monkeypatch.setattr(
            repository, "count_countries_with_values", lambda *_a: 5
        )
        monkeypatch.setattr(
            repository,
            "publish_definition",
            lambda *_a, **_kw: _definition(status="published"),
        )
        monkeypatch.setattr(helpers, "_audit", lambda *_a, **_kw: None)
        monkeypatch.setattr(helpers, "_track_event", lambda *_a, **_kw: None)

        result = service.approve_definition(
            CONNECTION, current_user=MODERATOR, definition_id="d-1"
        )
        assert result["status"] == "published"

    def test_reject_rejects_moderator_who_is_the_author(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_definition_by_id", lambda *_a: _definition()
        )
        author_as_moderator = CurrentUser(
            id=AUTHOR_ID,
            email="author@example.local",
            display_name="Author",
            role="moderator",
            status="active",
        )
        with pytest.raises(HTTPException) as exc_info:
            service.reject_definition(
                CONNECTION,
                current_user=author_as_moderator,
                definition_id="d-1",
                reason="not relevant",
            )
        _assert_error(exc_info, "moderation_conflict_of_interest")


class TestValues:
    def test_bulk_upsert_rejects_value_without_source_or_experience(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_definition_for_author", lambda *_a: _definition()
        )

        with pytest.raises(HTTPException) as exc_info:
            service.bulk_upsert_values(
                CONNECTION,
                current_user=AUTHOR,
                definition_id="d-1",
                items=[
                    AuthorMetricValueItem(country_slug="uruguay", value=50.0)
                ],
            )
        assert exc_info.value.status_code == 422
        _assert_error(exc_info, "value_source_required")

    def test_bulk_upsert_rejects_value_out_of_scale(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_definition_for_author", lambda *_a: _definition()
        )

        with pytest.raises(HTTPException) as exc_info:
            service.bulk_upsert_values(
                CONNECTION,
                current_user=AUTHOR,
                definition_id="d-1",
                items=[
                    AuthorMetricValueItem(
                        country_slug="uruguay",
                        value=150.0,
                        is_personal_experience=True,
                    )
                ],
            )
        assert exc_info.value.status_code == 422
        _assert_error(exc_info, "value_out_of_scale")

    def test_bulk_upsert_succeeds_with_valid_values(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_definition_for_author", lambda *_a: _definition()
        )
        monkeypatch.setattr(
            "app.repositories.countries.get_active_country_by_slug",
            lambda *_a: {
                "id": "country-1",
                "slug": "uruguay",
                "name": "Uruguay",
            },
        )
        monkeypatch.setattr(repository, "upsert_value", lambda *_a, **_kw: None)
        monkeypatch.setattr(
            repository,
            "list_values_for_definition",
            lambda *_a: [
                {
                    "id": "value-1",
                    "metric_id": "d-1",
                    "country_id": "country-1",
                    "country_slug": "uruguay",
                    "country_name": "Uruguay",
                    "value": 42.0,
                    "source_url": "https://example.com",
                    "is_personal_experience": False,
                    "note": None,
                    "valid_as_of": None,
                    "updated_at": "2026-01-01T00:00:00Z",
                }
            ],
        )
        monkeypatch.setattr(helpers, "_audit", lambda *_a, **_kw: None)

        result = service.bulk_upsert_values(
            CONNECTION,
            current_user=AUTHOR,
            definition_id="d-1",
            items=[
                AuthorMetricValueItem(
                    country_slug="uruguay",
                    value=42.0,
                    source_url="https://example.com",
                )
            ],
        )
        assert result["total"] == 1
        assert result["items"][0]["country_slug"] == "uruguay"

    def test_bulk_upsert_rejects_duplicate_country_slug(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_definition_for_author", lambda *_a: _definition()
        )
        upsert_calls: list[Any] = []
        monkeypatch.setattr(
            repository,
            "upsert_value",
            lambda *_a, **_kw: upsert_calls.append(1),
        )

        with pytest.raises(HTTPException) as exc_info:
            service.bulk_upsert_values(
                CONNECTION,
                current_user=AUTHOR,
                definition_id="d-1",
                items=[
                    AuthorMetricValueItem(
                        country_slug="uruguay",
                        value=10.0,
                        is_personal_experience=True,
                    ),
                    AuthorMetricValueItem(
                        country_slug="uruguay",
                        value=90.0,
                        is_personal_experience=True,
                    ),
                ],
            )
        assert exc_info.value.status_code == 422
        _assert_error(exc_info, "duplicate_country_slug")
        assert upsert_calls == []


class TestForks:
    def test_fork_rejects_unpublished_source(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_definition_by_id", lambda *_a: _definition()
        )

        with pytest.raises(HTTPException) as exc_info:
            service.fork_definition(
                CONNECTION,
                current_user=AUTHOR,
                source_definition_id="d-1",
                slug="my-fork",
            )
        assert exc_info.value.status_code == 404

    def test_fork_rejects_published_but_private_source(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository,
            "get_definition_by_id",
            lambda *_a: _definition(status="published", visibility="private"),
        )

        with pytest.raises(HTTPException) as exc_info:
            service.fork_definition(
                CONNECTION,
                current_user=AUTHOR,
                source_definition_id="d-1",
                slug="my-fork",
            )
        assert exc_info.value.status_code == 404

    def test_fork_copies_definition_and_sets_lineage(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        source = _definition(
            id="source-1", status="published", visibility="public"
        )
        monkeypatch.setattr(
            repository, "get_definition_by_id", lambda *_a: source
        )
        monkeypatch.setattr(
            repository, "get_definition_by_author_slug", lambda *_a: None
        )
        captured: dict[str, Any] = {}

        def fake_create(_conn: Any, **kwargs: Any) -> dict[str, Any]:
            captured.update(kwargs)
            return _definition(
                id="fork-1", forked_from_id="source-1", visibility="private"
            )

        monkeypatch.setattr(repository, "create_definition", fake_create)
        monkeypatch.setattr(helpers, "_audit", lambda *_a, **_kw: None)
        monkeypatch.setattr(helpers, "_track_event", lambda *_a, **_kw: None)

        result = service.fork_definition(
            CONNECTION,
            current_user=AUTHOR,
            source_definition_id="source-1",
            slug="my-fork",
        )
        assert result["forked_from_id"] == "source-1"
        assert captured["forked_from_id"] == "source-1"
        assert captured["visibility"] == "private"


class TestSubscriptions:
    def test_create_subscription_requires_exactly_one_target(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)

        with pytest.raises(HTTPException) as exc_info:
            service.create_subscription(
                CONNECTION,
                current_user=AUTHOR,
                metric_id="d-1",
                author_user_id="other-author",
            )
        assert exc_info.value.status_code == 422
        _assert_error(exc_info, "invalid_subscription_target")

    def test_create_subscription_rejects_unpublished_metric(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_definition_by_id", lambda *_a: _definition()
        )

        with pytest.raises(HTTPException) as exc_info:
            service.create_subscription(
                CONNECTION,
                current_user=AUTHOR,
                metric_id="d-1",
                author_user_id=None,
            )
        assert exc_info.value.status_code == 404

    def test_delete_subscription_rejects_when_not_owned(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "list_subscriptions_for_user", lambda *_a: []
        )

        with pytest.raises(HTTPException) as exc_info:
            service.delete_subscription(
                CONNECTION, current_user=AUTHOR, subscription_id="sub-1"
            )
        assert exc_info.value.status_code == 404
        _assert_error(exc_info, "subscription_not_found")


class TestOverlay:
    def test_get_author_metrics_for_country_returns_404_when_country_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            "app.repositories.countries.get_active_country_by_slug",
            lambda *_a: None,
        )

        with pytest.raises(HTTPException) as exc_info:
            service.get_author_metrics_for_country(CONNECTION, "nowhere")
        assert exc_info.value.status_code == 404


class TestReputationScoring:
    def test_compute_coverage_score_ratio(self) -> None:
        score = reputation_service.compute_coverage_score(
            published_metric_count=2, total_values=10, active_country_count=10
        )
        assert score == 50.0

    def test_compute_coverage_score_zero_when_no_published_metrics(
        self,
    ) -> None:
        score = reputation_service.compute_coverage_score(
            published_metric_count=0, total_values=0, active_country_count=10
        )
        assert score == 0.0

    def test_compute_freshness_score_fresh_within_window(self) -> None:
        now = datetime(2026, 6, 1, tzinfo=UTC)
        last_updated = datetime(2026, 5, 1, tzinfo=UTC)
        assert (
            reputation_service.compute_freshness_score(last_updated, now)
            == 100.0
        )

    def test_compute_freshness_score_stale_when_missing(self) -> None:
        now = datetime(2026, 6, 1, tzinfo=UTC)
        assert reputation_service.compute_freshness_score(None, now) == 0.0

    def test_compute_sourcing_score_ratio(self) -> None:
        score = reputation_service.compute_sourcing_score(
            sourced_values=3, total_values=4
        )
        assert score == 75.0

    def test_compute_and_store_reputation_dry_run_does_not_persist(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            feature_flags_service, "is_feature_enabled_by_key", lambda *_: True
        )
        monkeypatch.setattr(
            repository,
            "get_reputation_inputs_for_author",
            lambda *_a: {
                "published_metric_count": 1,
                "total_values": 5,
                "sourced_values": 5,
                "active_country_count": 10,
                "last_value_updated_at": None,
            },
        )
        monkeypatch.setattr(
            repository, "count_subscribers_for_author", lambda *_a: 3
        )
        stored: list[Any] = []
        monkeypatch.setattr(
            repository,
            "upsert_author_reputation",
            lambda *_a, **_kw: stored.append(1),
        )

        result = reputation_service.compute_and_store_reputation_for_author(
            CONNECTION, AUTHOR_ID, dry_run=True
        )
        assert result["computed"] is True
        assert result["stored"] is False
        assert stored == []
