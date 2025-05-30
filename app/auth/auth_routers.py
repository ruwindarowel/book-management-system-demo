from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import timedelta, datetime

from .auth_schemas import UserCreateModel, UserModel, UserLoginModel, UserBookModel
from .auth_service import AuthService
from ..db.db_main import get_session
from ..db.redis import add_jti_to_blocklist
from .auth_utils import create_access_token, decode_token, verify_password
from app.config import Config
from .auth_dependencies import (
    AccessTokenBearer,
    RefreshTokenBearer,
    get_current_user,
    RoleChecker,
)

auth_router = APIRouter(tags=["User Creation & Authentication"])
auth_service = AuthService()
access_token_bearer = AccessTokenBearer()
refresh_token_bearer = RefreshTokenBearer()
role_checker = RoleChecker(["admin", "user"])


@auth_router.post(
    "/sign_up/", response_model=UserModel, status_code=status.HTTP_201_CREATED
)
async def create_user_account(
    user_data: UserCreateModel, session: AsyncSession = Depends(get_session)
):
    email = user_data.email
    username = user_data.username

    user_exists = await auth_service.user_exists(email, username, session)

    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User with email or username already Exists",
        )

    new_user = await auth_service.create_user(user_data, session)

    return new_user


@auth_router.post("/login/")
async def login_user(
    login_data: UserLoginModel, session: AsyncSession = Depends(get_session)
):
    email = login_data.email
    password = login_data.password

    user = await auth_service.get_user_by_email(email, session)

    if user is not None:
        password_valid = verify_password(password, user.password_hash)

        if password_valid:
            access_token = create_access_token(
                user_data={
                    "email": user.email,
                    "user_uid": str(user.uid),
                    "role": str(user.role),
                }
            )

            refresh_token = create_access_token(
                user_data={"email": user.email, "user_uid": str(user.uid)},
                refresh=True,
                expiry=timedelta(minutes=Config.REFRESH_TOKEN_EXPIRY),
            )

            return JSONResponse(
                content={
                    "message": "Login Successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "email": user.email,
                        "uid": str(user.uid),
                    },
                }
            )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Invalid email or password"
    )


@auth_router.get("/refresh_token/")
async def get_new_access_token(token_details: dict = Depends(refresh_token_bearer)):
    expiry_timestamp = token_details["exp"]
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(user_data=token_details["user"])

        return JSONResponse(content={"access_token": new_access_token})

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Expired Token")
    # print(expiry_timestamp)


@auth_router.get("/logout")
async def revoke_token(token_details: dict = Depends(access_token_bearer)):
    jti = token_details["jti"]

    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={"message": "Successfully Logged Out"}, status_code=status.HTTP_200_OK
    )


@auth_router.get("/me/", response_model=UserBookModel)
async def get_current_user(
    user=Depends(get_current_user), _: bool = Depends(role_checker)
):
    return user
