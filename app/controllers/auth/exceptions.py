from fastapi import HTTPException


class TokenExpiredException(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Истек срок действия токена!")


class JWTParseErrorException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=403,
            detail="Произошла ошибка при считывании JWT-токена!",
        )
