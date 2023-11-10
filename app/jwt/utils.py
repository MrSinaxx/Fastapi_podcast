from datetime import datetime
from jose import JWTError, ExpiredSignatureError
from typing import Union, Any
from jose import jwt
import jose
from app.db.db import RedisDB
from app.core.config import settings
from fastapi import HTTPException, status


async def delete_refresh_token(token):
    payload = jwt.decode(
        token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]
    )
    user_id = payload["user_id"]
    jti = payload["jti"]
    redis = RedisDB()
    result = redis.get_data(key=f"user_{user_id} | {jti}")
    if result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User was logged out !!")
    redis.delete_data(key=f"user_{user_id} | {jti}")


def get_user_id_from_token(token: str) -> Union[str, None]:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload.get("user_id")
    except jose.ExpiredSignatureError:
        return None
    except jose.JWTError:
        return None


def is_access_token_valid(token: str) -> bool:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        expiration_time = datetime.utcfromtimestamp(payload["exp"])
        if expiration_time <= datetime.utcnow():
            return False

        user_id = payload.get("user_id")
        jti = payload.get("jti")
        redis = RedisDB()
        refresh_token_valid = redis.get_data(key=f"user_{user_id} | {jti}")

        return bool(refresh_token_valid)
    except ExpiredSignatureError:
        return False
    except JWTError:
        return False
