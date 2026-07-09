from app.core.auth import CurrentUser
from app.core.database import get_connection
from app.core.rbac import require_editor
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
from app.schemas.country_onboarding import AllCountriesOnboardingResult
from app.schemas.data_quality import DataQualityReport
from app.schemas.translations import (
    TranslationJobCreate,
    TranslationJobResponse,
)
from app.services import admin_content
from app.services.country_onboarding import evaluate_all_mvp_countries
from app.services.data_quality import build_data_quality_report
from fastapi import APIRouter, Depends
from psycopg import Connection
from typing import Annotated, Any
from uuid import UUID


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
def admin_create_source(
    payload: SourceCreate,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_editor)],
) -> AdminSourceResponse:
    row = admin_content.create_source(connection, payload, current_user.email)
    connection.commit()
    return AdminSourceResponse(item=row)


@router.patch(
    "/sources/{source_id}",
    response_model=AdminSourceResponse,
    responses=ADMIN_RESPONSES,
)
def admin_patch_source(
    source_id: UUID,
    payload: SourcePatch,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_editor)],
) -> AdminSourceResponse:
    row = admin_content.patch_source(
        connection, str(source_id), payload, current_user.email
    )
    connection.commit()
    return AdminSourceResponse(item=row)


@router.post(
    "/evidence-items",
    response_model=AdminEvidenceItemResponse,
    status_code=201,
    responses=ADMIN_RESPONSES,
)
def admin_create_evidence_item(
    payload: EvidenceItemCreate,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_editor)],
) -> AdminEvidenceItemResponse:
    row = admin_content.create_evidence_item(
        connection, payload, current_user.email
    )
    connection.commit()
    return AdminEvidenceItemResponse(item=row)


@router.patch(
    "/evidence-items/{evidence_item_id}",
    response_model=AdminEvidenceItemResponse,
    responses=ADMIN_RESPONSES,
)
def admin_patch_evidence_item(
    evidence_item_id: UUID,
    payload: EvidenceItemPatch,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_editor)],
) -> AdminEvidenceItemResponse:
    row = admin_content.patch_evidence_item(
        connection, str(evidence_item_id), payload, current_user.email
    )
    connection.commit()
    return AdminEvidenceItemResponse(item=row)


@router.post(
    "/legal-signals",
    response_model=AdminLegalSignalResponse,
    status_code=201,
    responses=ADMIN_RESPONSES,
)
def admin_create_legal_signal(
    payload: LegalSignalCreate,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_editor)],
) -> AdminLegalSignalResponse:
    row = admin_content.create_legal_signal(
        connection, payload, current_user.email
    )
    connection.commit()
    return AdminLegalSignalResponse(item=row)


@router.patch(
    "/legal-signals/{signal_id}",
    response_model=AdminLegalSignalResponse,
    responses=ADMIN_RESPONSES,
)
def admin_patch_legal_signal(
    signal_id: UUID,
    payload: LegalSignalPatch,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_editor)],
) -> AdminLegalSignalResponse:
    row = admin_content.patch_legal_signal(
        connection, str(signal_id), payload, current_user.email
    )
    connection.commit()
    return AdminLegalSignalResponse(item=row)


@router.patch(
    "/countries/{country_slug}/profile",
    response_model=AdminCountryProfileResponse,
    responses=ADMIN_RESPONSES,
)
def admin_patch_country_profile(
    country_slug: str,
    payload: CountryProfilePatch,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_editor)],
) -> AdminCountryProfileResponse:
    row = admin_content.patch_country_profile(
        connection, country_slug, payload, current_user.email
    )
    connection.commit()
    return AdminCountryProfileResponse(item=row)


@router.post(
    "/user-stories",
    response_model=AdminUserStoryResponse,
    status_code=201,
    responses=ADMIN_RESPONSES,
)
def admin_create_user_story(
    payload: UserStoryAdminCreate,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_editor)],
) -> AdminUserStoryResponse:
    row = admin_content.create_user_story(
        connection, payload, current_user.email
    )
    connection.commit()
    return AdminUserStoryResponse(item=row)


@router.patch(
    "/user-stories/{story_id}",
    response_model=AdminUserStoryResponse,
    responses=ADMIN_RESPONSES,
)
def admin_patch_user_story(
    story_id: UUID,
    payload: UserStoryPatch,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_editor)],
) -> AdminUserStoryResponse:
    row = admin_content.patch_user_story(
        connection, str(story_id), payload, current_user.email
    )
    connection.commit()
    return AdminUserStoryResponse(item=row)


@router.post(
    "/translations/jobs",
    response_model=TranslationJobResponse,
    status_code=201,
    responses=ADMIN_RESPONSES,
)
def admin_create_translation_job(
    payload: TranslationJobCreate,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_editor)],
) -> TranslationJobResponse:
    row = create_translation_job(connection, payload)
    connection.commit()
    return TranslationJobResponse(item=row)


@router.get(
    "/data-quality/report",
    response_model=DataQualityReport,
    responses={401: {"model": ErrorResponse}},
)
def admin_read_data_quality_report(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_editor)],
) -> DataQualityReport:
    return build_data_quality_report(connection)


@router.get(
    "/country-onboarding/report",
    response_model=AllCountriesOnboardingResult,
    responses={401: {"model": ErrorResponse}},
)
def admin_read_country_onboarding_report(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_editor)],
) -> AllCountriesOnboardingResult:
    return evaluate_all_mvp_countries(connection)
