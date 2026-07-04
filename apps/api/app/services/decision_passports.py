import hashlib
import secrets
from app.core.errors import api_error
from app.repositories import decision_passports as repository
from app.schemas.decision_engine import DecisionRunRequest, DecisionRunResponse
from app.schemas.decision_passports import (
    DecisionPassportCreateResponse,
    DecisionPassportMethodologySnapshot,
    DecisionPassportResponse,
    DecisionPassportSourceRef,
)
from app.schemas.decision_personalization import DecisionWeightItem
from app.services import decision_engine
from datetime import UTC, datetime, timedelta
from psycopg import Connection
from typing import Any


DISCLAIMER = (
    "This is not legal, tax, immigration, or investment advice. "
    "Verify every claim with qualified professionals before acting."
)

PASSPORT_PATH_PREFIX = "/decision/passports"
LEGACY_METHODOLOGY_VERSION = "legacy-inline-v1"


def _generate_token() -> tuple[str, str, str]:
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    return raw_token, token_hash, raw_token[:8]


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _collect_source_ids(decision_result: DecisionRunResponse) -> list[str]:
    source_ids: set[str] = set()
    for result in decision_result.results:
        for source in result.sources:
            source_ids.add(source.id)
    return sorted(source_ids)


def _build_methodology_snapshot(
    decision_result: DecisionRunResponse, payload: DecisionRunRequest
) -> DecisionPassportMethodologySnapshot:
    return DecisionPassportMethodologySnapshot(
        decision_engine_version=decision_result.meta.model_version,
        methodology_version=decision_result.methodology_version,
        scenario_slug=decision_result.scenario.slug,
        persona_slug=payload.persona,
        origin_country_slug=payload.origin_country_slug,
        weight_profile_id=decision_result.personalization.weight_profile_id,
        weight_profile_name=decision_result.personalization.weight_profile_name,
        custom_weights_applied=decision_result.personalization.custom_weights_applied,
        weight_mode=decision_result.personalization.weight_mode,
        applied_weights=[
            DecisionWeightItem(
                criterion=item.criterion,
                weight=item.weight,
            )
            for item in decision_result.personalization.effective_weights
        ],
        ranking_policy=decision_result.ranking_mode,
        disclaimer=DISCLAIMER,
        generated_at=decision_result.meta.generated_at,
    )


def create_decision_passport(
    connection: Connection[Any],
    decision_request: DecisionRunRequest,
    locale: str,
    expires_in_days: int | None,
    current_user_id: str | None = None,
) -> DecisionPassportCreateResponse:
    if current_user_id is None:
        decision_result = decision_engine.run_decision(
            connection, decision_request
        )
    else:
        decision_result = decision_engine.run_decision(
            connection,
            decision_request,
            current_user_id=current_user_id,
        )
    selected_country_slug = (
        decision_result.results[0].country.slug
        if decision_result.results
        else None
    )
    source_ids = _collect_source_ids(decision_result)
    methodology_snapshot = _build_methodology_snapshot(
        decision_result, decision_request
    )
    raw_token, token_hash, token_prefix = _generate_token()
    generated_at = datetime.now(UTC)
    expires_at = (
        generated_at + timedelta(days=expires_in_days)
        if expires_in_days is not None
        else None
    )
    row = repository.create_decision_passport(
        connection,
        public_token_hash=token_hash,
        public_token_prefix=token_prefix,
        locale=locale,
        scenario_slug=decision_result.scenario.slug,
        persona_slug=decision_request.persona,
        origin_country_slug=decision_request.origin_country_slug,
        candidate_country_slugs=list(decision_request.candidate_country_slugs),
        selected_country_slug=selected_country_slug,
        decision_request=decision_request.model_dump(mode="json"),
        decision_result_snapshot=decision_result.model_dump(mode="json"),
        methodology_snapshot=methodology_snapshot.model_dump(mode="json"),
        source_ids=source_ids,
        route_ids=[],
        disclaimer=DISCLAIMER,
        expires_at=expires_at,
    )
    connection.commit()
    return DecisionPassportCreateResponse(
        passport_id=str(row["id"]),
        token=raw_token,
        path=f"{PASSPORT_PATH_PREFIX}/{raw_token}",
        expires_at=row.get("expires_at"),
        generated_at=row["generated_at"],
    )


def _source_refs(
    decision_result: DecisionRunResponse, source_ids: list[str]
) -> list[DecisionPassportSourceRef]:
    wanted = set(source_ids)
    refs: dict[str, DecisionPassportSourceRef] = {}
    for result in decision_result.results:
        for source in result.sources:
            if source.id in wanted and source.id not in refs:
                refs[source.id] = DecisionPassportSourceRef(
                    id=source.id, title=source.title, url=source.url
                )
    return [refs[source_id] for source_id in source_ids if source_id in refs]


def _decision_result_from_snapshot(
    snapshot: dict[str, Any],
) -> DecisionRunResponse:
    data = dict(snapshot)
    meta = dict(data.get("meta") or {})
    methodology_version = str(
        data.get("methodology_version")
        or meta.get("methodology_version")
        or LEGACY_METHODOLOGY_VERSION
    )
    meta["methodology_version"] = methodology_version
    data["meta"] = meta
    data["methodology_version"] = methodology_version
    return DecisionRunResponse.model_validate(data)


def _methodology_snapshot_from_snapshot(
    snapshot: dict[str, Any],
    decision_result: DecisionRunResponse,
) -> DecisionPassportMethodologySnapshot:
    data = dict(snapshot)
    data.setdefault("methodology_version", decision_result.methodology_version)
    data.setdefault(
        "weight_profile_id", decision_result.personalization.weight_profile_id
    )
    data.setdefault(
        "weight_profile_name",
        decision_result.personalization.weight_profile_name,
    )
    data.setdefault(
        "applied_weights",
        [
            item.model_dump(mode="json")
            for item in decision_result.personalization.effective_weights
        ],
    )
    return DecisionPassportMethodologySnapshot.model_validate(data)


def get_decision_passport_by_token(
    connection: Connection[Any], token: str
) -> DecisionPassportResponse:
    token_hash = _hash_token(token)
    row = repository.get_decision_passport_by_token_hash(connection, token_hash)
    if row is None:
        raise api_error(
            404,
            "decision_passport_not_found",
            "Decision passport was not found.",
        )
    status = str(row["status"])
    expires_at = row.get("expires_at")
    if (
        status == "active"
        and expires_at is not None
        and expires_at < datetime.now(UTC)
    ):
        status = "expired"
    if status == "revoked":
        raise api_error(
            410,
            "decision_passport_revoked",
            "Decision passport has been revoked.",
        )
    if status == "expired":
        raise api_error(
            410,
            "decision_passport_expired",
            "Decision passport has expired.",
        )
    decision_result = _decision_result_from_snapshot(
        row["decision_result_snapshot"]
    )
    methodology_snapshot = _methodology_snapshot_from_snapshot(
        row["methodology_snapshot"], decision_result
    )
    source_ids = [str(item) for item in row.get("source_ids") or []]
    route_ids = [str(item) for item in row.get("route_ids") or []]
    return DecisionPassportResponse(
        id=str(row["id"]),
        locale=row["locale"],
        scenario_slug=row["scenario_slug"],
        persona_slug=row.get("persona_slug"),
        origin_country_slug=row.get("origin_country_slug"),
        candidate_country_slugs=[
            str(item) for item in row.get("candidate_country_slugs") or []
        ],
        selected_country_slug=row.get("selected_country_slug"),
        decision_result=decision_result,
        methodology_version=methodology_snapshot.methodology_version,
        methodology_snapshot=methodology_snapshot,
        source_ids=source_ids,
        route_ids=route_ids,
        source_refs=_source_refs(decision_result, source_ids),
        route_refs=[],
        disclaimer=row["disclaimer"],
        generated_at=row["generated_at"],
        expires_at=row.get("expires_at"),
        status=status,
    )
