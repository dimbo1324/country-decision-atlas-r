from app.core.auth import CurrentUser
from app.core.database import get_connection
from app.core.rbac import require_user
from app.schemas.weight_profiles import (
    UserWeightProfile,
    UserWeightProfileCreate,
    UserWeightProfileListResponse,
    UserWeightProfilePatch,
    UserWeightProfileResponse,
)
from app.services import weight_profiles as service
from fastapi import APIRouter, Depends, status
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(prefix="/me/weight-profiles", tags=["weight-profiles"])


@router.get("", response_model=UserWeightProfileListResponse)
def list_weight_profiles(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_user)],
) -> UserWeightProfileListResponse:
    return UserWeightProfileListResponse(
        items=[
            UserWeightProfile(**item)
            for item in service.list_user_weight_profiles(
                connection, current_user.id
            )
        ]
    )


@router.get("/{profile_id}", response_model=UserWeightProfileResponse)
def get_weight_profile(
    profile_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_user)],
) -> UserWeightProfileResponse:
    profile = service.get_user_weight_profile(
        connection, profile_id, current_user.id
    )
    return UserWeightProfileResponse(item=UserWeightProfile(**profile))


@router.post(
    "",
    response_model=UserWeightProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_weight_profile(
    payload: UserWeightProfileCreate,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_user)],
) -> UserWeightProfileResponse:
    profile = service.create_user_weight_profile(
        connection,
        user_id=current_user.id,
        name=payload.name,
        scenario_slug=payload.scenario_slug,
        weights=payload.weights,
        is_default=payload.is_default,
    )
    connection.commit()
    return UserWeightProfileResponse(item=UserWeightProfile(**profile))


@router.patch("/{profile_id}", response_model=UserWeightProfileResponse)
def update_weight_profile(
    profile_id: str,
    payload: UserWeightProfilePatch,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_user)],
) -> UserWeightProfileResponse:
    profile = service.update_user_weight_profile(
        connection,
        user_id=current_user.id,
        profile_id=profile_id,
        fields=payload.model_fields_set,
        name=payload.name,
        scenario_slug=payload.scenario_slug,
        weights=payload.weights,
        is_default=payload.is_default,
    )
    connection.commit()
    return UserWeightProfileResponse(item=UserWeightProfile(**profile))


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_weight_profile(
    profile_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_user)],
) -> None:
    service.delete_user_weight_profile(
        connection, profile_id=profile_id, user_id=current_user.id
    )
    connection.commit()
