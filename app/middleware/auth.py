from fastapi import HTTPException, Header
from typing import Annotated, Optional
from config.env import config


class AuthMiddleware:
    """Authentication middleware for string-based auth"""

    @staticmethod
    def verify_auth_string(
        x_auth_string: Annotated[Optional[str], Header()] = None,
    ) -> str:
        """
        Verify the authentication string from header.

        Args:
            x_auth_string: The authentication string from X-Auth-String header

        Returns:
            The validated authentication string

        Raises:
            HTTPException: If authentication fails
        """
        if not x_auth_string:
            raise HTTPException(
                status_code=401,
                detail="Authentication string is required. Please provide X-Auth-String header.",
            )

        if x_auth_string != config.AUTH_STRING:
            raise HTTPException(status_code=401, detail="Invalid authentication string")

        return x_auth_string


# Create instance for easy import
auth_middleware = AuthMiddleware()
