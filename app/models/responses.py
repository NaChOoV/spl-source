from pydantic import BaseModel
from typing import Optional, Dict, Any


class ApiResponse(BaseModel):
    """Standard API response model"""

    message: str
    data: Optional[Dict[str, Any]] = None
    authenticated: bool = False


class UserResponse(BaseModel):
    """User response model"""

    user_id: int
    message: str
    authenticated: bool = True


class CreateDataRequest(BaseModel):
    """Request model for creating data"""

    name: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CreateDataResponse(BaseModel):
    """Response model for created data"""

    id: int
    message: str
    data: CreateDataRequest
    authenticated: bool = True
