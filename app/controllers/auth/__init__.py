from app.controllers.auth.dto import AccessJWTPayloadDto
from jose import ExpiredSignatureError, JWTError, jwt
from pydantic import BaseModel
from os import environ
from .exceptions import (
    JWTParseErrorException,
    TokenExpiredException,
)


JWT_SECRET = environ.get("JWT_SECRET", "dstu")


class UserJWTDto(BaseModel):
    access_token: str
    refresh_token: str


def get_user_dto(token: str) -> AccessJWTPayloadDto:
    try:
        raw_payload = jwt.decode(token, JWT_SECRET)
        return AccessJWTPayloadDto(**raw_payload)
    except ExpiredSignatureError:
        raise TokenExpiredException()
    except JWTError:
        raise JWTParseErrorException()
