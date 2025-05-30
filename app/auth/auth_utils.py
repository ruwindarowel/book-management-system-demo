from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt
import uuid
import logging

from app.config import Config

password_context = CryptContext(schemes=["bcrypt"], deprecated=["auto"])


def generate_password_hash(password) -> str:
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


# CREATING JWT TOKENS
def create_access_token(
    user_data: dict,
    expiry: timedelta = timedelta(minutes=30),
    refresh: bool = False,
):
    expire = datetime.now(timezone.utc) + expiry
    payload = {
        "sub": str(user_data.get("email")),  # ✅ must be a string
        "user": user_data,  # ✅ store full user info here
        "exp": expire,
        "jti": str(uuid.uuid4()),
        "refresh": refresh,
    }
    token = jwt.encode(payload, key=Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)
    return token


def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token, key=Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM]
        )

        return token_data

    except jwt.PyJWTError as e:
        logging.exception(e)
        return None
