from app.api.v1.feature_flags import router
from app.core.config import Settings, get_settings
from app.core.database import get_connection
from app.repositories import feature_flags as repository
from app.schemas.feature_flags import FeatureAccessContext, FeatureAccessTier
from app.services import feature_flags as service
from fastapi import FastAPI
from fastapi.testclient import TestClient
from psycopg import Connection
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())


def _feature(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "key": "analytics_enabled",
        "name": "Analytics",
        "description": "Analytics",
        "status": "enabled",
        "access_tier": "public",
        "default_enabled": True,
        "metadata": {},
        "created_at": None,
        "updated_at": None,
    }
    data.update(overrides)
    return data


def _rule(
    feature_key: str, access_tier: str, is_enabled: bool = True
) -> dict[str, Any]:
    return {
        "feature_key": feature_key,
        "access_tier": access_tier,
        "is_enabled": is_enabled,
        "metadata": {},
        "created_at": None,
    }


def _client(monkeypatch: Any, features: list[dict[str, Any]]) -> TestClient:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_connection] = lambda: CONNECTION
    app.dependency_overrides[get_settings] = lambda: Settings(app_env="local")
    monkeypatch.setattr(repository, "list_feature_flags", lambda *_: features)
    monkeypatch.setattr(
        repository,
        "list_all_feature_access_rules",
        lambda *_: [
            _rule(
                str(feature["key"]),
                str(feature["access_tier"]),
                bool(feature["default_enabled"]),
            )
            for feature in features
        ],
    )
    monkeypatch.setattr(
        repository,
        "get_feature_flag",
        lambda _conn, key: next(
            (feature for feature in features if feature["key"] == key), None
        ),
    )
    monkeypatch.setattr(
        repository,
        "list_feature_access_rules",
        lambda _conn, key: [
            _rule(
                str(feature["key"]),
                str(feature["access_tier"]),
                bool(feature["default_enabled"]),
            )
            for feature in features
            if feature["key"] == key
        ],
    )
    return TestClient(app)


def test_list_features_returns_seeded_flags(monkeypatch: Any) -> None:
    client = _client(
        monkeypatch,
        [_feature(), _feature(key="data_journal_enabled", name="Data journal")],
    )
    response = client.get("/api/v1/platform/features")
    assert response.status_code == 200
    keys = {item["key"] for item in response.json()["items"]}
    assert {"analytics_enabled", "data_journal_enabled"}.issubset(keys)


def test_analytics_enabled_accessible_for_public(monkeypatch: Any) -> None:
    client = _client(monkeypatch, [_feature()])
    body = client.get("/api/v1/platform/features/analytics_enabled").json()
    assert body["item"]["is_enabled_for_context"] is True
    assert body["decision"]["reason"] == "feature_enabled"


def test_disabled_feature_is_not_accessible_for_public(monkeypatch: Any) -> None:
    client = _client(monkeypatch, [_feature(status="disabled", default_enabled=False)])
    body = client.get("/api/v1/platform/features/analytics_enabled").json()
    assert body["item"]["is_enabled_for_context"] is False
    assert body["decision"]["reason"] == "feature_disabled"


def test_internal_feature_access(monkeypatch: Any) -> None:
    client = _client(
        monkeypatch,
        [
            _feature(
                key="redis_cache_enabled",
                status="internal",
                access_tier="internal",
                default_enabled=True,
            )
        ],
    )
    public_body = client.get("/api/v1/platform/features/redis_cache_enabled").json()
    internal_body = client.get(
        "/api/v1/platform/features/redis_cache_enabled?access_tier=internal"
    ).json()
    admin_body = client.get(
        "/api/v1/platform/features/redis_cache_enabled?access_tier=admin"
    ).json()
    assert public_body["item"]["is_enabled_for_context"] is False
    assert internal_body["item"]["is_enabled_for_context"] is True
    assert admin_body["item"]["is_enabled_for_context"] is True


def test_deprecated_feature_is_always_false(monkeypatch: Any) -> None:
    client = _client(monkeypatch, [_feature(status="deprecated")])
    body = client.get(
        "/api/v1/platform/features/analytics_enabled?access_tier=admin"
    ).json()
    assert body["item"]["is_enabled_for_context"] is False


def test_unknown_feature_detail_returns_404(monkeypatch: Any) -> None:
    client = _client(monkeypatch, [])
    response = client.get("/api/v1/platform/features/missing")
    assert response.status_code == 404
    assert response.json()["detail"]["error"]["code"] == "feature_not_found"


def test_can_access_is_deterministic() -> None:
    context = FeatureAccessContext(access_tier=FeatureAccessTier.public)
    feature = _feature()
    rules = [_rule("analytics_enabled", "public")]
    first = service.can_access(context, feature, rules, "analytics_enabled")
    second = service.can_access(context, feature, rules, "analytics_enabled")
    assert first == second


def test_invalid_access_tier_returns_422(monkeypatch: Any) -> None:
    client = _client(monkeypatch, [_feature()])
    response = client.get("/api/v1/platform/features?access_tier=partner")
    assert response.status_code == 422


def test_tier_hierarchy_for_beta_internal_admin() -> None:
    feature = _feature(
        key="beta_feature",
        access_tier="beta",
        default_enabled=True,
    )
    rules = [_rule("beta_feature", "beta")]
    public = FeatureAccessContext(access_tier=FeatureAccessTier.public)
    beta = FeatureAccessContext(access_tier=FeatureAccessTier.beta)
    internal = FeatureAccessContext(access_tier=FeatureAccessTier.internal)
    assert (
        service.can_access(public, feature, rules, "beta_feature").is_enabled is False
    )
    assert service.can_access(beta, feature, rules, "beta_feature").is_enabled is True
    assert (
        service.can_access(internal, feature, rules, "beta_feature").is_enabled is True
    )
