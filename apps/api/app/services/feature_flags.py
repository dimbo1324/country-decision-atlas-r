from app.core.config import Settings
from app.schemas.feature_flags import (
    FeatureAccessContext,
    FeatureAccessDecision,
    FeatureAccessTier,
    FeatureFlag,
    FeatureFlagStatus,
)
from typing import Any


TIER_ORDER = {
    FeatureAccessTier.public: 0,
    FeatureAccessTier.beta: 1,
    FeatureAccessTier.internal: 2,
    FeatureAccessTier.admin: 3,
}


def default_access_context(
    settings: Settings, access_tier: FeatureAccessTier = FeatureAccessTier.public
) -> FeatureAccessContext:
    environment = "local" if settings.app_env == "local" else "production"
    return FeatureAccessContext(
        access_tier=access_tier,
        environment=environment,
        is_admin=access_tier == FeatureAccessTier.admin,
    )


def can_access(
    context: FeatureAccessContext,
    feature: dict[str, Any] | None,
    rules: list[dict[str, Any]],
    feature_key: str,
) -> FeatureAccessDecision:
    if feature is None:
        return FeatureAccessDecision(
            feature_key=feature_key,
            is_enabled=False,
            reason="feature_not_found",
            access_tier=context.access_tier,
            status=None,
        )
    status = FeatureFlagStatus(str(feature["status"]))
    if status == FeatureFlagStatus.disabled:
        return _decision(feature_key, False, "feature_disabled", context, status)
    if status == FeatureFlagStatus.deprecated:
        return _decision(feature_key, False, "feature_deprecated", context, status)
    if status == FeatureFlagStatus.internal:
        allowed = context.access_tier in {
            FeatureAccessTier.internal,
            FeatureAccessTier.admin,
        }
        return _decision(
            feature_key,
            allowed,
            "feature_enabled" if allowed else "feature_internal_only",
            context,
            status,
        )
    feature_tier = FeatureAccessTier(str(feature["access_tier"]))
    if context.is_admin:
        return _decision(feature_key, True, "feature_enabled", context, status)
    if not _tier_allowed(context.access_tier, feature_tier):
        return _decision(feature_key, False, "tier_not_allowed", context, status)
    if not rules:
        enabled = bool(feature["default_enabled"])
        return _decision(
            feature_key,
            enabled,
            "feature_enabled" if enabled else "feature_rule_disabled",
            context,
            status,
        )
    matching = [
        rule
        for rule in rules
        if _tier_allowed(
            context.access_tier, FeatureAccessTier(str(rule["access_tier"]))
        )
    ]
    enabled = any(bool(rule["is_enabled"]) for rule in matching)
    return _decision(
        feature_key,
        enabled,
        "feature_enabled" if enabled else "feature_rule_disabled",
        context,
        status,
    )


def feature_response(
    feature: dict[str, Any],
    decision: FeatureAccessDecision,
) -> FeatureFlag:
    return FeatureFlag(
        key=str(feature["key"]),
        name=str(feature["name"]),
        description=feature.get("description"),
        status=FeatureFlagStatus(str(feature["status"])),
        access_tier=FeatureAccessTier(str(feature["access_tier"])),
        default_enabled=bool(feature["default_enabled"]),
        is_enabled_for_context=decision.is_enabled,
        decision_reason=decision.reason,
    )


def _tier_allowed(requested: FeatureAccessTier, required: FeatureAccessTier) -> bool:
    return TIER_ORDER[requested] >= TIER_ORDER[required]


def _decision(
    feature_key: str,
    is_enabled: bool,
    reason: str,
    context: FeatureAccessContext,
    status: FeatureFlagStatus,
) -> FeatureAccessDecision:
    return FeatureAccessDecision(
        feature_key=feature_key,
        is_enabled=is_enabled,
        reason=reason,
        access_tier=context.access_tier,
        status=status,
    )
