"""Sources and evidence are seeded and routed to the countries/routes that cite them."""

from tests.test_openapi_contract import load_contract
from tests.test_seed_data import SEED_SQL, SOURCE_DEPTH_SQL


def test_sources_and_evidence_are_seeded_and_routed() -> None:
    paths = load_contract()["paths"]

    assert "/api/v1/sources" in paths
    assert "/api/v1/sources/{source_id}/evidence" in paths
    assert SEED_SQL.count("https://") >= 20
    assert "decision_evidence" in SEED_SQL


def test_source_depth_adds_country_source_coverage() -> None:
    assert SOURCE_DEPTH_SQL.count("('russia',") >= 10
    assert SOURCE_DEPTH_SQL.count("('uruguay',") >= 10
    assert "https://www.consultant.ru/document/cons_doc_LAW_37868/" in SOURCE_DEPTH_SQL
    assert "https://www.gub.uy/tramites/residencia-legal-temporaria" in SOURCE_DEPTH_SQL
    assert "ON CONFLICT (url) DO UPDATE" in SOURCE_DEPTH_SQL
