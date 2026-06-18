from app.core.admin_auth import require_admin_token
from app.core.database import get_connection
from app.repositories.translations import create_translation_job
from app.schemas.admin_content import (
    AdminCountryProfileResponse,
    AdminEvidenceItemResponse,
    AdminLegalSignalResponse,
    AdminSourceResponse,
    AdminUserStoryResponse,
    CountryProfilePatch,
    EvidenceItemCreate,
    EvidenceItemPatch,
    LegalSignalCreate,
    LegalSignalPatch,
    SourceCreate,
    SourcePatch,
    UserStoryAdminCreate,
    UserStoryPatch,
)
from app.schemas.common import ContentValidationError, ErrorResponse
from app.schemas.translations import TranslationJobCreate, TranslationJobResponse
from app.services import admin_content
from fastapi import APIRouter, Depends
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(prefix="/admin", tags=["admin"])


ADMIN_RESPONSES: dict[int | str, dict[str, Any]] = {
    401: {"model": ErrorResponse},
    422: {"model": ContentValidationError},
}


@router.post(
    "/sources",
    response_model=AdminSourceResponse,
    status_code=201,
    responses=ADMIN_RESPONSES,
)
async def admin_create_source(
    payload: SourceCreate,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    changed_by: Annotated[str, Depends(require_admin_token)],
) -> AdminSourceResponse:
    row = admin_content.create_source(connection, payload, changed_by)
    connection.commit()
    return AdminSourceResponse(item=row)


@router.patch(
    "/sources/{source_id}",
    response_model=AdminSourceResponse,
    responses=ADMIN_RESPONSES,
)
async def admin_patch_source(
    source_id: str,
    payload: SourcePatch,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    changed_by: Annotated[str, Depends(require_admin_token)],
) -> AdminSourceResponse:
    row = admin_content.patch_source(connection, source_id, payload, changed_by)
    connection.commit()
    return AdminSourceResponse(item=row)


@router.post(
    "/evidence-items",
    response_model=AdminEvidenceItemResponse,
    status_code=201,
    responses=ADMIN_RESPONSES,
)
async def admin_create_evidence_item(
    payload: EvidenceItemCreate,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    changed_by: Annotated[str, Depends(require_admin_token)],
) -> AdminEvidenceItemResponse:
    row = admin_content.create_evidence_item(connection, payload, changed_by)
    connection.commit()
    return AdminEvidenceItemResponse(item=row)


@router.patch(
    "/evidence-items/{evidence_item_id}",
    response_model=AdminEvidenceItemResponse,
    responses=ADMIN_RESPONSES,
)
async def admin_patch_evidence_item(
    evidence_item_id: str,
    payload: EvidenceItemPatch,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    changed_by: Annotated[str, Depends(require_admin_token)],
) -> AdminEvidenceItemResponse:
    row = admin_content.patch_evidence_item(
        connection, evidence_item_id, payload, changed_by
    )
    connection.commit()
    return AdminEvidenceItemResponse(item=row)


@router.post(
    "/legal-signals",
    response_model=AdminLegalSignalResponse,
    status_code=201,
    responses=ADMIN_RESPONSES,
)
async def admin_create_legal_signal(
    payload: LegalSignalCreate,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    changed_by: Annotated[str, Depends(require_admin_token)],
) -> AdminLegalSignalResponse:
    row = admin_content.create_legal_signal(connection, payload, changed_by)
    connection.commit()
    return AdminLegalSignalResponse(item=row)


@router.patch(
    "/legal-signals/{signal_id}",
    response_model=AdminLegalSignalResponse,
    responses=ADMIN_RESPONSES,
)
async def admin_patch_legal_signal(
    signal_id: str,
    payload: LegalSignalPatch,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    changed_by: Annotated[str, Depends(require_admin_token)],
) -> AdminLegalSignalResponse:
    row = admin_content.patch_legal_signal(connection, signal_id, payload, changed_by)
    connection.commit()
    return AdminLegalSignalResponse(item=row)


@router.patch(
    "/countries/{country_slug}/profile",
    response_model=AdminCountryProfileResponse,
    responses=ADMIN_RESPONSES,
)
async def admin_patch_country_profile(
    country_slug: str,
    payload: CountryProfilePatch,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    changed_by: Annotated[str, Depends(require_admin_token)],
) -> AdminCountryProfileResponse:
    row = admin_content.patch_country_profile(
        connection, country_slug, payload, changed_by
    )
    connection.commit()
    return AdminCountryProfileResponse(item=row)


@router.post(
    "/user-stories",
    response_model=AdminUserStoryResponse,
    status_code=201,
    responses=ADMIN_RESPONSES,
)
async def admin_create_user_story(
    payload: UserStoryAdminCreate,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    changed_by: Annotated[str, Depends(require_admin_token)],
) -> AdminUserStoryResponse:
    row = admin_content.create_user_story(connection, payload, changed_by)
    connection.commit()
    return AdminUserStoryResponse(item=row)


@router.patch(
    "/user-stories/{story_id}",
    response_model=AdminUserStoryResponse,
    responses=ADMIN_RESPONSES,
)
async def admin_patch_user_story(
    story_id: str,
    payload: UserStoryPatch,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    changed_by: Annotated[str, Depends(require_admin_token)],
) -> AdminUserStoryResponse:
    row = admin_content.patch_user_story(connection, story_id, payload, changed_by)
    connection.commit()
    return AdminUserStoryResponse(item=row)


@router.post(
    "/translations/jobs",
    response_model=TranslationJobResponse,
    status_code=201,
    responses=ADMIN_RESPONSES,
)
async def admin_create_translation_job(
    payload: TranslationJobCreate,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[str, Depends(require_admin_token)],
) -> TranslationJobResponse:
    row = create_translation_job(connection, payload)
    connection.commit()
    return TranslationJobResponse(item=row)
