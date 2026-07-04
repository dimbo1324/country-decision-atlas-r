"""Runtime read-model bootstrap script: ordered platform-then-trust execution and failure propagation."""

import scripts.bootstrap_runtime_read_models as bootstrap
from app.schemas.platform_metrics import PlatformMetricsRecomputeSummary
from typing import Any


class FakeConnection:
    def __init__(self) -> None:
        self.commits = 0

    def __enter__(self) -> "FakeConnection":
        return self

    def __exit__(self, *_args: Any) -> None:
        return None

    def commit(self) -> None:
        self.commits += 1


def _platform_summary(
    *,
    feature_enabled: bool = True,
    metrics_failed: int = 0,
) -> PlatformMetricsRecomputeSummary:
    return PlatformMetricsRecomputeSummary(
        feature_enabled=feature_enabled,
        dry_run=False,
        countries_requested=3,
        countries_processed=3,
        countries_skipped=0,
        metrics_computed=21,
        metrics_written=21,
        metrics_failed=metrics_failed,
        errors=[],
    )


def test_bootstrap_runtime_read_models_runs_platform_then_trust(
    monkeypatch: Any, capsys: Any
) -> None:
    conn = FakeConnection()
    calls: list[str] = []
    monkeypatch.setattr(
        bootstrap,
        "get_settings",
        lambda: type("Settings", (), {"database_url": "postgresql://test"})(),
    )

    def fake_platform(
        *_args: Any, **_kwargs: Any
    ) -> PlatformMetricsRecomputeSummary:
        calls.append("platform")
        return _platform_summary()

    def fake_trust(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
        calls.append("trust")
        return {
            "feature_enabled": True,
            "countries_failed": 0,
            "countries_processed": 3,
        }

    monkeypatch.setattr(bootstrap, "connect", lambda *_a, **_kw: conn)
    monkeypatch.setattr(
        bootstrap,
        "compute_platform_metrics_for_all_countries",
        fake_platform,
    )
    monkeypatch.setattr(
        bootstrap,
        "compute_and_store_trust_for_all_countries",
        fake_trust,
    )

    assert bootstrap.main([]) == 0
    assert calls == ["platform", "trust"]
    assert conn.commits == 2
    assert '"ok": true' in capsys.readouterr().out


def test_bootstrap_runtime_read_models_stops_when_platform_fails(
    monkeypatch: Any,
) -> None:
    conn = FakeConnection()
    calls: list[str] = []
    monkeypatch.setattr(
        bootstrap,
        "get_settings",
        lambda: type("Settings", (), {"database_url": "postgresql://test"})(),
    )

    def fake_platform(
        *_args: Any, **_kwargs: Any
    ) -> PlatformMetricsRecomputeSummary:
        calls.append("platform")
        return _platform_summary(metrics_failed=1)

    def fake_trust(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
        calls.append("trust")
        return {}

    monkeypatch.setattr(bootstrap, "connect", lambda *_a, **_kw: conn)
    monkeypatch.setattr(
        bootstrap,
        "compute_platform_metrics_for_all_countries",
        fake_platform,
    )
    monkeypatch.setattr(
        bootstrap,
        "compute_and_store_trust_for_all_countries",
        fake_trust,
    )

    assert bootstrap.main([]) == 1
    assert calls == ["platform"]
    assert conn.commits == 0


def test_bootstrap_runtime_read_models_fails_when_trust_disabled(
    monkeypatch: Any,
) -> None:
    conn = FakeConnection()
    monkeypatch.setattr(
        bootstrap,
        "get_settings",
        lambda: type("Settings", (), {"database_url": "postgresql://test"})(),
    )
    monkeypatch.setattr(
        bootstrap,
        "compute_platform_metrics_for_all_countries",
        lambda *_a, **_kw: _platform_summary(),
    )
    monkeypatch.setattr(bootstrap, "connect", lambda *_a, **_kw: conn)
    monkeypatch.setattr(
        bootstrap,
        "compute_and_store_trust_for_all_countries",
        lambda *_a, **_kw: {"feature_enabled": False, "countries_failed": 0},
    )

    assert bootstrap.main([]) == 1
    assert conn.commits == 2
