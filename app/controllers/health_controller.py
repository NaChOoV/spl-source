from fastapi import APIRouter
from app.models.responses import ApiResponse

router = APIRouter(prefix="", tags=["health"])


@router.get("/", response_model=ApiResponse)
async def health_check():
    """
    Health check endpoint - no authentication required

    Returns:
        ApiResponse: Basic health status
    """
    return ApiResponse(
        message="Hello from spl-source API! Server is running.",
        data={"status": "healthy", "version": "0.1.0"},
        authenticated=False,
    )
