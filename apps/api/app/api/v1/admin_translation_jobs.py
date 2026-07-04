from app.core.auth import CurrentUser
from app.core.database import get_connection
from app.core.rbac import require_editor
from app.schemas.common import Pagination
from app.schemas.translation_jobs import (
    TranslationJobBatchResult,
    TranslationJobCreateMissingRequest,
    TranslationJobCreateResponse,
    TranslationJobCreateStaleRequest,
    TranslationJobItem,
    TranslationJobListResponse,
    TranslationJobProcessBatchRequest,
    TranslationJobProcessNextRequest,
    TranslationJobProcessResult,
    TranslationJobRetryFailedRequest,
    TranslationJobRetryFailedResponse,
)
from app.services import translation_jobs as svc
from app.services.translation_providers import get_translation_provider
from fastapi import APIRouter, Depends, Query
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(
    prefix="/admin/translation-jobs", tags=["admin-translation-jobs"]
)


@router.get("", response_model=TranslationJobListResponse)
def list_jobs(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_editor)],
    status: Annotated[
        str | None,
        Query(
            pattern="^(queued|running|pending|processing|completed|failed|cancelled)$"
        ),
    ] = None,
    target_locale: Annotated[str | None, Query(pattern="^[a-z]{2}$")] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> TranslationJobListResponse:
    data = svc.list_jobs(connection, status, target_locale, limit, offset)
    items = [TranslationJobItem.model_validate(i) for i in data["items"]]
    return TranslationJobListResponse(
        items=items,
        pagination=Pagination(total=data["total"], limit=limit, offset=offset),
    )


@router.post(
    "/create-missing",
    response_model=TranslationJobCreateResponse,
    status_code=201,
)
def create_missing(
    payload: TranslationJobCreateMissingRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_editor)],
) -> TranslationJobCreateResponse:
    jobs = svc.discover_missing_jobs(
        connection, payload.target_locale, payload.limit, payload.priority
    )
    items = [TranslationJobItem.model_validate(j) for j in jobs]
    return TranslationJobCreateResponse(created_count=len(items), items=items)


@router.post(
    "/create-stale",
    response_model=TranslationJobCreateResponse,
    status_code=201,
)
def create_stale(
    payload: TranslationJobCreateStaleRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_editor)],
) -> TranslationJobCreateResponse:
    jobs = svc.discover_stale_jobs(
        connection, payload.target_locale, payload.limit, payload.priority
    )
    items = [TranslationJobItem.model_validate(j) for j in jobs]
    return TranslationJobCreateResponse(created_count=len(items), items=items)


@router.post("/process-next", response_model=TranslationJobProcessResult)
def process_next(
    payload: TranslationJobProcessNextRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_editor)],
) -> TranslationJobProcessResult:
    provider = get_translation_provider()
    result = svc.process_next_job(
        connection,
        payload.worker_id,
        payload.target_locale,
        provider,
        payload.dry_run,
    )
    if result is None:
        if not payload.dry_run:
            connection.commit()
        return TranslationJobProcessResult(job_id="", status="no_pending_jobs")
    if result.get("status") != "dry_run":
        connection.commit()
    return TranslationJobProcessResult.model_validate(result)


@router.post("/process-batch", response_model=TranslationJobBatchResult)
def process_batch(
    payload: TranslationJobProcessBatchRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_editor)],
) -> TranslationJobBatchResult:
    provider = get_translation_provider()
    result = svc.process_batch(
        connection,
        payload.worker_id,
        payload.target_locale,
        payload.limit,
        provider,
        payload.dry_run,
    )
    results = [
        TranslationJobProcessResult.model_validate(r) for r in result["results"]
    ]
    return TranslationJobBatchResult(
        processed=result["processed"],
        completed=result["completed"],
        failed=result["failed"],
        results=results,
    )


@router.post(
    "/retry-failed",
    response_model=TranslationJobRetryFailedResponse,
    status_code=200,
)
def retry_failed(
    payload: TranslationJobRetryFailedRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_editor)],
) -> TranslationJobRetryFailedResponse:
    jobs = svc.retry_failed_jobs(
        connection, payload.target_locale, payload.limit
    )
    connection.commit()
    items = [TranslationJobItem.model_validate(j) for j in jobs]
    return TranslationJobRetryFailedResponse(
        reset_count=len(items), items=items
    )
