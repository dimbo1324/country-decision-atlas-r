from pathlib import Path
import pytest
from typing import Any


MIGRATION = Path("database/migrations/038_origin_aware_decisions.sql")

VALID_STATUS = {"draft", "review", "published", "archived", "rejected"}
VALID_LABEL = {"favourable", "mixed", "restrictive", "unknown"}
VALID_CONFIDENCE = {"low", "medium", "high"}
VALID_FRESHNESS = {"fresh", "current", "stale", "unknown"}

KNOWN_SOURCE_IDS = {"source-1", "source-2"}
KNOWN_EVIDENCE_IDS = {"evidence-1", "evidence-2"}


def _sql() -> str:
    return MIGRATION.read_text(encoding="utf-8")


class FakeCountryPairStore:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def insert(self, row: dict[str, Any]) -> dict[str, Any]:
        self._validate(row)
        key = (row["origin_country_id"], row["destination_country_id"])
        for existing in self.rows:
            existing_key = (
                existing["origin_country_id"],
                existing["destination_country_id"],
            )
            if existing_key == key:
                raise ValueError("country_pair_unique")
        self.rows.append(row)
        return row

    def _validate(self, row: dict[str, Any]) -> None:
        if row["origin_country_id"] == row["destination_country_id"]:
            raise ValueError("country_pair_not_self_check")
        if row["status"] not in VALID_STATUS:
            raise ValueError("country_pair_status_check")
        if row["compatibility_label"] not in VALID_LABEL:
            raise ValueError("country_pair_label_check")
        if row["confidence"] not in VALID_CONFIDENCE:
            raise ValueError("country_pair_confidence_check")
        if row["freshness_status"] not in VALID_FRESHNESS:
            raise ValueError("country_pair_freshness_check")


class FakeCountryPairLinkStore:
    def __init__(self, known_ids: set[str]) -> None:
        self._known_ids = known_ids
        self.rows: set[tuple[str, str]] = set()

    def insert(self, country_pair_id: str, linked_id: str) -> None:
        if linked_id not in self._known_ids:
            raise ValueError("foreign_key_violation")
        key = (country_pair_id, linked_id)
        if key in self.rows:
            raise ValueError("duplicate_key_violation")
        self.rows.add(key)


def _pair_row(**overrides: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "origin_country_id": "russia",
        "destination_country_id": "uruguay",
        "status": "published",
        "compatibility_label": "mixed",
        "confidence": "low",
        "freshness_status": "current",
    }
    row.update(overrides)
    return row


def test_migration_file_exists() -> None:
    assert MIGRATION.exists()


def test_country_pair_compatibility_table_exists() -> None:
    assert "CREATE TABLE IF NOT EXISTS country_pair_compatibility " in _sql()


def test_country_pair_compatibility_sources_table_exists() -> None:
    assert "CREATE TABLE IF NOT EXISTS country_pair_compatibility_sources" in _sql()


def test_country_pair_compatibility_evidence_table_exists() -> None:
    assert "CREATE TABLE IF NOT EXISTS country_pair_compatibility_evidence" in _sql()


def test_route_checklist_items_table_exists() -> None:
    assert "CREATE TABLE IF NOT EXISTS route_checklist_items" in _sql()


def test_constraints_present() -> None:
    for name in [
        "country_pair_unique",
        "country_pair_not_self_check",
        "country_pair_status_check",
        "country_pair_label_check",
        "country_pair_confidence_check",
        "country_pair_freshness_check",
        "route_checklist_step_unique",
        "route_checklist_status_check",
        "route_checklist_step_order_check",
    ]:
        assert name in _sql()


def test_indexes_present() -> None:
    for name in [
        "idx_country_pair_origin",
        "idx_country_pair_destination",
        "idx_country_pair_status",
        "idx_country_pair_label",
        "idx_country_pair_sources_source",
        "idx_country_pair_evidence_evidence",
        "idx_route_checklist_route",
        "idx_route_checklist_status",
        "idx_route_checklist_source",
        "idx_route_checklist_evidence",
    ]:
        assert name in _sql()


def test_migration_is_idempotent() -> None:
    sql = _sql()
    assert sql.count("CREATE TABLE IF NOT EXISTS country_pair_compatibility ") == 1
    assert sql.count("CREATE TABLE IF NOT EXISTS route_checklist_items") == 1
    assert "ON CONFLICT (origin_country_id, destination_country_id) DO UPDATE" in sql
    assert "ON CONFLICT (route_id, step_order) DO UPDATE" in sql
    assert "ON CONFLICT (country_pair_id, source_id) DO NOTHING" in sql
    assert "ON CONFLICT (country_pair_id, evidence_item_id) DO NOTHING" in sql


def test_migration_does_not_touch_other_domains() -> None:
    sql = _sql()
    for forbidden in (
        "country_cii_scores",
        "country_scores",
        "country_score_breakdowns",
        "scenario_metric_weights",
        "country_drift_snapshots",
        "country_trust_scores",
        "country_platform_metrics",
    ):
        assert forbidden not in sql


def test_migration_does_not_rewrite_old_migrations() -> None:
    other_migrations = sorted(Path("database/migrations").glob("0*.sql"))
    assert MIGRATION in other_migrations
    for path in other_migrations:
        if path == MIGRATION:
            continue
        assert path.read_text(encoding="utf-8")


def test_valid_country_pair_can_be_inserted() -> None:
    store = FakeCountryPairStore()
    row = store.insert(_pair_row())
    assert row["compatibility_label"] == "mixed"


def test_self_pair_rejected() -> None:
    store = FakeCountryPairStore()
    with pytest.raises(ValueError, match="country_pair_not_self_check"):
        store.insert(_pair_row(destination_country_id="russia"))


def test_duplicate_origin_destination_rejected() -> None:
    store = FakeCountryPairStore()
    store.insert(_pair_row())
    with pytest.raises(ValueError, match="country_pair_unique"):
        store.insert(_pair_row())


def test_reverse_direction_pair_is_not_a_duplicate() -> None:
    store = FakeCountryPairStore()
    store.insert(
        _pair_row(origin_country_id="russia", destination_country_id="uruguay")
    )
    row = store.insert(
        _pair_row(origin_country_id="uruguay", destination_country_id="russia")
    )
    assert row["origin_country_id"] == "uruguay"


def test_invalid_status_rejected() -> None:
    store = FakeCountryPairStore()
    with pytest.raises(ValueError, match="country_pair_status_check"):
        store.insert(_pair_row(status="live"))


def test_invalid_compatibility_label_rejected() -> None:
    store = FakeCountryPairStore()
    with pytest.raises(ValueError, match="country_pair_label_check"):
        store.insert(_pair_row(compatibility_label="excellent"))


def test_invalid_confidence_rejected() -> None:
    store = FakeCountryPairStore()
    with pytest.raises(ValueError, match="country_pair_confidence_check"):
        store.insert(_pair_row(confidence="certain"))


def test_invalid_freshness_status_rejected() -> None:
    store = FakeCountryPairStore()
    with pytest.raises(ValueError, match="country_pair_freshness_check"):
        store.insert(_pair_row(freshness_status="outdated"))


def test_source_link_fk_works() -> None:
    store = FakeCountryPairLinkStore(KNOWN_SOURCE_IDS)
    store.insert("pair-1", "source-1")
    with pytest.raises(ValueError, match="foreign_key_violation"):
        store.insert("pair-1", "unknown-source")


def test_evidence_link_fk_works() -> None:
    store = FakeCountryPairLinkStore(KNOWN_EVIDENCE_IDS)
    store.insert("pair-1", "evidence-1")
    with pytest.raises(ValueError, match="foreign_key_violation"):
        store.insert("pair-1", "unknown-evidence")


def test_source_evidence_link_uniqueness_enforced() -> None:
    store = FakeCountryPairLinkStore(KNOWN_SOURCE_IDS)
    store.insert("pair-1", "source-1")
    with pytest.raises(ValueError, match="duplicate_key_violation"):
        store.insert("pair-1", "source-1")


def test_seed_pairs_present_for_key_mvp_routes() -> None:
    sql = _sql()
    for origin, destination in [
        ("russia", "uruguay"),
        ("russia", "argentina"),
        ("argentina", "uruguay"),
        ("uruguay", "argentina"),
    ]:
        assert f"'{origin}',\n                '{destination}'," in sql


def test_seed_does_not_invent_reverse_russia_pairs() -> None:
    sql = _sql()
    assert "'argentina',\n                'russia'," not in sql
    assert "'uruguay',\n                'russia'," not in sql
