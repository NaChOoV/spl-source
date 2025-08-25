from fastapi import APIRouter, Depends
from app.middleware.auth import auth_middleware
from app.services.source_service import SourceService
from app.models.user import AbmUser
from fastapi import Response, HTTPException

# Create service instance
source_service = SourceService()

router = APIRouter(
    prefix="/user",
    tags=["user"],
    dependencies=[Depends(auth_middleware.verify_auth_string)],
)


@router.get("/abm/{run}", response_model=AbmUser | None)
async def get_abm_user(run: str):
    """
    Get user by RUN - requires authentication

    Args:
        run: The RUN of the user to retrieve

    Returns:
        AbmUser: User data from ABM or empty dict
    """

    abm_user = source_service.get_abm_user_by_run(run)

    if abm_user is None:
        return Response(status_code=200)

    return abm_user


@router.get("/{external_id}")
async def get_user(external_id: int):
    """
    Get user by external ID - requires authentication

    Args:
        external_id: The external ID of the user to retrieve (non-empty string)

    Returns:
        User: User data from ABM or empty dict
    """

    user = source_service.get_user_by_external_id(external_id)

    if user is None:
        return Response(status_code=200)

    return user


@router.get("/{run}/inbody")
async def get_user_inbody(run: str):
    """
    Get user's in-body information by RUN - requires authentication

    Args:
        run: The RUN of the user to retrieve

    Returns:
        AbmUser: User data from ABM or empty dict
    """

    abm_user = source_service.get_abm_user_by_run(run)
    if abm_user is None:
        raise HTTPException(status_code=404, detail={"code": "USER_NOT_FOUND"})

    inbody = source_service.get_inbody_by_external_id(abm_user.external_id)

    return {"data": inbody}
