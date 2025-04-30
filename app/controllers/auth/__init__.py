from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.controllers.auth.dto import AccessJWTPayloadDto
from jose import ExpiredSignatureError, JWTError, jwt
from pydantic import BaseModel
from fastapi import Depends
from os import environ

from .exceptions import (
    InvalidTokenException,
    JWTParseErrorException,
    TokenExpiredException,
)


JWT_SECRET = environ.get("JWT_SECRET", "dstu")
SECURITY_SCHEME = HTTPBearer(auto_error=False)


class UserJWTDto(BaseModel):
    access_token: str
    refresh_token: str


def get_token_from_header(
    credentials: HTTPAuthorizationCredentials = Depends(SECURITY_SCHEME),
) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise InvalidTokenException()
    return credentials.credentials


def get_user_dto_from_token(token: str) -> AccessJWTPayloadDto:
    try:
        raw_payload = jwt.decode(token, JWT_SECRET)
        return AccessJWTPayloadDto(**raw_payload)
    except ExpiredSignatureError:
        raise TokenExpiredException()
    except JWTError:
        raise JWTParseErrorException()


async def get_user_dto(
    token: str = Depends(get_token_from_header),
) -> AccessJWTPayloadDto:
    try:
        raw_payload = jwt.decode(token, JWT_SECRET)
        return AccessJWTPayloadDto(**raw_payload)
    except ExpiredSignatureError:
        raise TokenExpiredException()
    except JWTError:
        raise JWTParseErrorException()
