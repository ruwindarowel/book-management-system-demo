from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.exceptions import HTTPException
from fastapi import Request, status, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List, Any

from .auth_utils import decode_token
from app.db.redis import token_in_blocklist
from app.db.db_main import get_session
from .auth_service import AuthService
from ..db.models import User
import logging

logger = logging.getLogger(__name__)
user_service = AuthService()


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        creds: HTTPAuthorizationCredentials = await super().__call__(request)
        token = creds.credentials

        token_data = decode_token(token)

        # Ensure token has required fields
        required_fields = {"jti", "exp", "user", "refresh"}
        if not required_fields.issubset(token_data):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing required fields.",
            )

        self.verify_token_data(token_data)

        if not self.token_valid(token_data):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "This token is invalid or has expired",
                    "resolution": "Please get a new token",
                },
            )

        if await token_in_blocklist(token_data["jti"]):
            logger.warning(f"Blocked token used: jti={token_data['jti']}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "This token is invalid or has been revoked",
                    "resolution": "Please get a new token",
                },
            )

        return token_data

    def token_valid(self, token_data: dict) -> bool:
        return token_data is not None

    def verify_token_data(self, token_data):
        raise NotImplementedError("Please override this method in the child classes.")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict):
        if "refresh" not in token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing 'refresh' claim.",
            )
        if token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access token required, not refresh token.",
            )


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict):
        if "refresh" not in token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing 'refresh' claim.",
            )
        if not token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Refresh token required, not access token.",
            )


async def get_current_user(
    token_details: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session),
):
    user_email = token_details["user"]["email"]

    user = await user_service.get_user_by_email(user_email, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found for given token",
        )
    return user


class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> Any:
        if current_user.role in self.allowed_roles:
            return True
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to perform this action",
        )
