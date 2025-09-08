from fastapi import APIRouter, Depends, HTTPException
from app.models.responses import ApiResponse
from app.services.source_service import SourceService
from app.middleware.auth import auth_middleware

router = APIRouter(
    prefix="/access",
    tags=["access"],
    dependencies=[Depends(auth_middleware.verify_auth_string)],
)

# Create service instance
source_service = SourceService()


@router.get("", response_model=ApiResponse)
async def get_today_access():
    """
    Get today's access data from source system - requires authentication

    Returns:
        ApiResponse: Today's access data
    """
    try:
        access_data = await source_service.get_today_access()
        return ApiResponse(
            message="Today's access data retrieved successfully",
            data={
                "records": [record.model_dump(by_alias=True) for record in access_data],
                "count": len(access_data) if access_data else 0,
            },
            authenticated=True,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
