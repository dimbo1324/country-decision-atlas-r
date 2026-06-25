from app.schemas.admin_content import LegalSignalCreate, LegalSignalPatch
from app.schemas.common import LegalStatus
from app.schemas.country_read_model import CountryReadModelLegalSignal
from app.schemas.decision_engine import LegalSignalDetail
from app.schemas.legal_signals import LegalSignal
from datetime import datetime
from pathlib import Path
from pydantic import ValidationError
import pytest
from tests.test_openapi_contract import load_contract
from uuid import uuid4


def legal_signal_payload() -> dict[str, object]:
    return {
        "id": uuid4(),
        "country_id": uuid4(),
        "title": "Residency update",
        "summary": "Summary",
        "signal_type": "law",
        "sentiment": "positive",
        "severity": "medium",
        "status": "published",
        "legal_status": "effective",
        "confidence_level": "high",
        "created_at": datetime(2026, 1, 1),
        "updated_at": datetime(2026, 1, 2),
    }


def test_public_legal_signal_schema_contains_legal_status() -> None:
    signal = LegalSignal.model_validate(legal_signal_payload())

    assert signal.legal_status == LegalStatus.effective


def test_legal_signal_detail_schema_contains_legal_status() -> None:
    payload = {
        **legal_signal_payload(),
        "impact_direction": "positive",
        "impact_level": "medium",
        "affected_groups": [],
        "source_id": uuid4(),
        "confidence": "medium",
    }

    signal = LegalSignalDetail.model_validate(payload)

    assert signal.legal_status == LegalStatus.effective


def test_country_legal_signal_schema_contains_legal_status() -> None:
    signal = CountryReadModelLegalSignal.model_validate(
        {
            "id": str(uuid4()),
            "title": "Residency update",
            "summary": "Summary",
            "signal_type": "residence",
            "impact_direction": "positive",
            "impact_level": "medium",
            "legal_status": "adopted",
        }
    )

    assert signal.legal_status == LegalStatus.adopted


def test_admin_create_and_patch_accept_valid_legal_status() -> None:
    created = LegalSignalCreate(country_slug="argentina", legal_status="effective")
    patched = LegalSignalPatch(legal_status="revoked")

    assert created.legal_status == LegalStatus.effective
    assert patched.legal_status == LegalStatus.revoked


def test_admin_legal_signal_rejects_invalid_legal_status() -> None:
    with pytest.raises(ValidationError):
        LegalSignalPatch(legal_status="active")


def test_openapi_contains_legal_status() -> None:
    schemas = load_contract()["components"]["schemas"]

    assert "LegalStatus" in schemas
    assert "legal_status" in schemas["LegalSignal"]["properties"]
    assert "legal_status" in schemas["LegalSignalDetail"]["properties"]
    assert "legal_status" in schemas["CountryReadModelLegalSignal"]["properties"]
    assert "legal_status" in schemas["LegalSignalCreate"]["properties"]
    assert "legal_status" in schemas["LegalSignalPatch"]["properties"]


def test_generated_typescript_contains_legal_status() -> None:
    generated = Path("packages/contracts/generated/types.ts").read_text(
        encoding="utf-8"
    )

    assert "LegalStatus" in generated
    assert "legal_status" in generated
