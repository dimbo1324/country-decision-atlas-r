from typing import Annotated, Any
from fastapi import APIRouter, Depends
from psycopg import Connection
from app.core.database import get_connection
from app.repositories.legal_signals import create_legal_signal
from app.repositories.translations import create_translation_job
from app.schemas.legal_signals import LegalSignalCreate, LegalSignalResponse
from app.schemas.translations import TranslationJobCreate, TranslationJobResponse
router = APIRouter(prefix="/admin", tags=["admin"])
@router.post("/legal-signals", response_model=LegalSignalResponse, status_code=201)
async def admin_create_legal_signal(
    payload: LegalSignalCreate,
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> LegalSignalResponse:
    row = create_legal_signal(connection, payload)
    connection.commit()
    return LegalSignalResponse(item=row)
@router.post("/translations/jobs", response_model=TranslationJobResponse, status_code=201)
async def admin_create_translation_job(
    payload: TranslationJobCreate,
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> TranslationJobResponse:
    row = create_translation_job(connection, payload)
    connection.commit()
    return TranslationJobResponse(item=row)
