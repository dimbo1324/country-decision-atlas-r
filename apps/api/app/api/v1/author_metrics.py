from app.core.auth import CurrentUser
from app.core.database import get_connection
from app.core.errors import api_error
from app.core.rbac import require_capability, require_user
from app.schemas.author_metrics import (
    ArchiveAuthorMetricResponse,
    AuthorMetricValueListResponse,
    AuthorReputationResponse,
    BulkUpsertAuthorMetricValuesRequest,
    CountryAuthorMetricsResponse,
    CreateAuthorMetricRequest,
    CreateSubscriptionRequest,
    ForkAuthorMetricRequest,
    MyAuthorMetricDefinition,
    MyAuthorMetricListResponse,
    PublicAuthorMetricListResponse,
    SubmitAuthorMetricResponse,
    SubscriptionFeedResponse,
    SubscriptionListResponse,
    SubscriptionResponse,
    UpdateAuthorMetricRequest,
)
from app.services import author_metrics as service
from app.services.capabilities import AUTHOR_METRICS
from fastapi import APIRouter, Depends, Query, status
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(tags=["author-metrics"])


@router.get(
    "/authors/{user_id}/metrics", response_model=PublicAuthorMetricListResponse
)
def list_author_public_metrics(
    user_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> dict[str, Any]:
    return service.list_public_definitions_for_author(connection, user_id)


@router.get(
    "/authors/{user_id}/reputation", response_model=AuthorReputationResponse
)
def get_author_reputation(
    user_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> dict[str, Any]:
    reputation = service.get_reputation_for_author(connection, user_id)
    if reputation is None:
        raise api_error(
            404,
            "author_reputation_not_found",
            "Author reputation has not been computed yet.",
            {},
        )
    return reputation


@router.get(
    "/countries/{country_slug}/author-metrics",
    response_model=CountryAuthorMetricsResponse,
)
def list_country_author_metrics(
    country_slug: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> dict[str, Any]:
    return service.get_author_metrics_for_country(connection, country_slug)


@router.get("/me/author-metrics", response_model=MyAuthorMetricListResponse)
def list_my_author_metrics(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[
        CurrentUser, Depends(require_capability(AUTHOR_METRICS))
    ],
) -> dict[str, Any]:
    return service.list_my_definitions(connection, current_user)


@router.post(
    "/me/author-metrics",
    response_model=MyAuthorMetricDefinition,
    status_code=status.HTTP_201_CREATED,
)
def create_my_author_metric(
    payload: CreateAuthorMetricRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[
        CurrentUser, Depends(require_capability(AUTHOR_METRICS))
    ],
) -> dict[str, Any]:
    definition = service.create_my_definition(
        connection, current_user=current_user, payload=payload
    )
    connection.commit()
    return definition


@router.get(
    "/me/author-metrics/{definition_id}",
    response_model=MyAuthorMetricDefinition,
)
def get_my_author_metric(
    definition_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[
        CurrentUser, Depends(require_capability(AUTHOR_METRICS))
    ],
) -> dict[str, Any]:
    return service.get_my_definition(
        connection, current_user=current_user, definition_id=definition_id
    )


@router.patch(
    "/me/author-metrics/{definition_id}",
    response_model=MyAuthorMetricDefinition,
)
def update_my_author_metric(
    definition_id: str,
    payload: UpdateAuthorMetricRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[
        CurrentUser, Depends(require_capability(AUTHOR_METRICS))
    ],
) -> dict[str, Any]:
    definition = service.update_my_definition(
        connection,
        current_user=current_user,
        definition_id=definition_id,
        payload=payload,
    )
    connection.commit()
    return definition


@router.post(
    "/me/author-metrics/{definition_id}/submit",
    response_model=SubmitAuthorMetricResponse,
)
def submit_my_author_metric(
    definition_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[
        CurrentUser, Depends(require_capability(AUTHOR_METRICS))
    ],
) -> dict[str, Any]:
    definition = service.submit_my_definition(
        connection, current_user=current_user, definition_id=definition_id
    )
    connection.commit()
    return {"definition": definition}


@router.post(
    "/me/author-metrics/{definition_id}/archive",
    response_model=ArchiveAuthorMetricResponse,
)
def archive_my_author_metric(
    definition_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[
        CurrentUser, Depends(require_capability(AUTHOR_METRICS))
    ],
) -> dict[str, Any]:
    definition = service.archive_my_definition(
        connection, current_user=current_user, definition_id=definition_id
    )
    connection.commit()
    return {"definition": definition}


@router.get(
    "/me/author-metrics/{definition_id}/values",
    response_model=AuthorMetricValueListResponse,
)
def list_my_author_metric_values(
    definition_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[
        CurrentUser, Depends(require_capability(AUTHOR_METRICS))
    ],
) -> dict[str, Any]:
    return service.list_values_for_my_definition(
        connection, current_user=current_user, definition_id=definition_id
    )


@router.put(
    "/me/author-metrics/{definition_id}/values",
    response_model=AuthorMetricValueListResponse,
)
def bulk_upsert_my_author_metric_values(
    definition_id: str,
    payload: BulkUpsertAuthorMetricValuesRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[
        CurrentUser, Depends(require_capability(AUTHOR_METRICS))
    ],
) -> dict[str, Any]:
    result = service.bulk_upsert_values(
        connection,
        current_user=current_user,
        definition_id=definition_id,
        items=payload.items,
    )
    connection.commit()
    return result


@router.post(
    "/author-metrics/{definition_id}/fork",
    response_model=MyAuthorMetricDefinition,
    status_code=status.HTTP_201_CREATED,
)
def fork_author_metric(
    definition_id: str,
    payload: ForkAuthorMetricRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[
        CurrentUser, Depends(require_capability(AUTHOR_METRICS))
    ],
) -> dict[str, Any]:
    definition = service.fork_definition(
        connection,
        current_user=current_user,
        source_definition_id=definition_id,
        slug=payload.slug,
    )
    connection.commit()
    return definition


@router.post(
    "/me/subscriptions",
    response_model=SubscriptionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_my_subscription(
    payload: CreateSubscriptionRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_user)],
) -> dict[str, Any]:
    subscription = service.create_subscription(
        connection,
        current_user=current_user,
        metric_id=payload.metric_id,
        author_user_id=payload.author_user_id,
    )
    connection.commit()
    return subscription


@router.delete("/me/subscriptions/{subscription_id}", status_code=204)
def delete_my_subscription(
    subscription_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_user)],
) -> None:
    service.delete_subscription(
        connection, current_user=current_user, subscription_id=subscription_id
    )
    connection.commit()


@router.get("/me/subscriptions", response_model=SubscriptionListResponse)
def list_my_subscriptions(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_user)],
) -> dict[str, Any]:
    return service.list_my_subscriptions(connection, current_user)


@router.get("/me/subscriptions/feed", response_model=SubscriptionFeedResponse)
def get_my_subscriptions_feed(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_user)],
    limit: int = Query(50, ge=1, le=200),
) -> dict[str, Any]:
    return service.list_my_feed(connection, current_user, limit=limit)
