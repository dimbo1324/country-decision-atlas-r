from app.core.config import Settings, get_settings
from app.core.database import get_connection
from app.core.errors import api_error
from app.repositories import feature_flags as repository
from app.schemas.feature_flags import (
    FeatureAccessRule,
    FeatureAccessTier,
    FeatureFlagDetailResponse,
    FeatureFlagListResponse,
)
from app.services import feature_flags as service
from fastapi import APIRouter, Depends, Query
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(prefix="/platform/features", tags=["platform"])


@router.get("", response_model=FeatureFlagListResponse)
def read_feature_flags(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    settings: Annotated[Settings, Depends(get_settings)],
    access_tier: Annotated[
        FeatureAccessTier, Query()
    ] = FeatureAccessTier.public,
) -> FeatureFlagListResponse:
    context = service.default_access_context(settings, access_tier)
    features = repository.list_feature_flags(connection)
    all_rules = repository.list_all_feature_access_rules(connection)
    rules_by_feature: dict[str, list[dict[str, Any]]] = {}
    for rule in all_rules:
        rules_by_feature.setdefault(str(rule["feature_key"]), []).append(rule)
    return FeatureFlagListResponse(
        items=[
            service.feature_response(
                feature,
                service.can_access(
                    context,
                    feature,
                    rules_by_feature.get(str(feature["key"]), []),
                    str(feature["key"]),
                ),
            )
            for feature in features
        ],
        context=context,
    )


@router.get("/{feature_key}", response_model=FeatureFlagDetailResponse)
def read_feature_flag(
    feature_key: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    settings: Annotated[Settings, Depends(get_settings)],
    access_tier: Annotated[
        FeatureAccessTier, Query()
    ] = FeatureAccessTier.public,
) -> FeatureFlagDetailResponse:
    context = service.default_access_context(settings, access_tier)
    feature = repository.get_feature_flag(connection, feature_key)
    rules = repository.list_feature_access_rules(connection, feature_key)
    decision = service.can_access(context, feature, rules, feature_key)
    if feature is None:
        raise api_error(
            404,
            "feature_not_found",
            "Feature flag not found.",
            {"feature_key": feature_key},
        )
    return FeatureFlagDetailResponse(
        item=service.feature_response(feature, decision),
        decision=decision,
        context=context,
        access_rules=[FeatureAccessRule.model_validate(rule) for rule in rules],
    )
