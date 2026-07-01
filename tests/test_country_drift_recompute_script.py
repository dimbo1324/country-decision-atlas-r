from app.services.country_drift import (
    CountryDriftBatchResult,
    CountryDriftStoredResult,
)
import psycopg
from scripts import recompute_country_drift
import sys
from unittest.mock import MagicMock


class FakeConnection:
    def __init__(self) -> None:
        self.committed = False

    def commit(self) -> None:
        self.committed = True

    def __enter__(self) -> "FakeConnection":
        return self

    def __exit__(self, *_args: object) -> None:
        return None


def _install_fake_connect(monkeypatch: MagicMock, conn: FakeConnection) -> None:
    monkeypatch.setattr(psycopg, "connect", lambda *_a, **_kw: conn)


def test_all_flag_calls_batch_and_prints_summary(
    monkeypatch: MagicMock, capsys: MagicMock
) -> None:
    conn = FakeConnection()
    _install_fake_connect(monkeypatch, conn)
    batch = CountryDriftBatchResult(
        countries_processed=3,
        snapshots_written=3,
        events_emitted=1,
        insufficient_data_count=0,
        errors=[],
    )
    monkeypatch.setattr(
        recompute_country_drift,
        "compute_and_store_all_country_drifts",
        lambda *_a, **_kw: batch,
    )
    monkeypatch.setattr(sys, "argv", ["recompute_country_drift.py", "--all"])
    exit_code = recompute_country_drift.main()
    assert exit_code == 0
    assert conn.committed is True
    captured = capsys.readouterr()
    assert "countries_processed" in captured.out
    assert "3" in captured.out


def test_all_flag_returns_nonzero_when_errors_present(
    monkeypatch: MagicMock,
) -> None:
    conn = FakeConnection()
    _install_fake_connect(monkeypatch, conn)
    batch = CountryDriftBatchResult(
        countries_processed=1,
        snapshots_written=0,
        events_emitted=0,
        insufficient_data_count=0,
        errors=[{"country_slug": "nowhere", "error": "boom"}],
    )
    monkeypatch.setattr(
        recompute_country_drift,
        "compute_and_store_all_country_drifts",
        lambda *_a, **_kw: batch,
    )
    monkeypatch.setattr(sys, "argv", ["recompute_country_drift.py", "--all"])
    exit_code = recompute_country_drift.main()
    assert exit_code == 1


def test_country_flag_calls_single_country(monkeypatch: MagicMock) -> None:
    conn = FakeConnection()
    _install_fake_connect(monkeypatch, conn)
    result = CountryDriftStoredResult(
        country_slug="argentina",
        country_not_found=False,
        dry_run=False,
        computed=True,
        stored=True,
        label="stable",
        previous_label=None,
        confidence="medium",
        net_score=None,
        event_count=5,
        event_emitted=False,
        error=None,
    )
    monkeypatch.setattr(
        recompute_country_drift,
        "compute_and_store_country_drift",
        lambda *_a, **_kw: result,
    )
    monkeypatch.setattr(
        sys, "argv", ["recompute_country_drift.py", "--country", "argentina"]
    )
    exit_code = recompute_country_drift.main()
    assert exit_code == 0
    assert conn.committed is True


def test_country_not_found_returns_nonzero(monkeypatch: MagicMock) -> None:
    conn = FakeConnection()
    _install_fake_connect(monkeypatch, conn)
    result = CountryDriftStoredResult(
        country_slug="nowhere",
        country_not_found=True,
        dry_run=False,
        computed=False,
        stored=False,
        label=None,
        previous_label=None,
        confidence=None,
        net_score=None,
        event_count=0,
        event_emitted=False,
        error=None,
    )
    monkeypatch.setattr(
        recompute_country_drift,
        "compute_and_store_country_drift",
        lambda *_a, **_kw: result,
    )
    monkeypatch.setattr(
        sys, "argv", ["recompute_country_drift.py", "--country", "nowhere"]
    )
    exit_code = recompute_country_drift.main()
    assert exit_code == 1


def test_dry_run_does_not_commit(monkeypatch: MagicMock) -> None:
    conn = FakeConnection()
    _install_fake_connect(monkeypatch, conn)
    batch = CountryDriftBatchResult(
        countries_processed=1,
        snapshots_written=0,
        events_emitted=0,
        insufficient_data_count=1,
        errors=[],
    )
    monkeypatch.setattr(
        recompute_country_drift,
        "compute_and_store_all_country_drifts",
        lambda *_a, **_kw: batch,
    )
    monkeypatch.setattr(
        sys, "argv", ["recompute_country_drift.py", "--all", "--dry-run"]
    )
    exit_code = recompute_country_drift.main()
    assert exit_code == 0
    assert conn.committed is False


def test_no_events_flag_disables_emit_events(monkeypatch: MagicMock) -> None:
    conn = FakeConnection()
    _install_fake_connect(monkeypatch, conn)
    captured_kwargs: dict[str, object] = {}

    def fake_batch(_conn: object, **kwargs: object) -> CountryDriftBatchResult:
        captured_kwargs.update(kwargs)
        return CountryDriftBatchResult(
            countries_processed=1,
            snapshots_written=1,
            events_emitted=0,
            insufficient_data_count=0,
            errors=[],
        )

    monkeypatch.setattr(
        recompute_country_drift, "compute_and_store_all_country_drifts", fake_batch
    )
    monkeypatch.setattr(
        sys, "argv", ["recompute_country_drift.py", "--all", "--no-events"]
    )
    exit_code = recompute_country_drift.main()
    assert exit_code == 0
    assert captured_kwargs["emit_events"] is False


def test_all_and_country_are_mutually_exclusive(monkeypatch: MagicMock) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["recompute_country_drift.py", "--all", "--country", "argentina"],
    )
    try:
        recompute_country_drift.main()
        raised = False
    except SystemExit:
        raised = True
    assert raised is True
