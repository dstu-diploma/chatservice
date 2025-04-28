from fastapi import HTTPException


class NoSuchActionException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Такого действия не существует!",
        )


class ActionValidationPayloadException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Произошла ошибка при валидации входных данных!",
        )
