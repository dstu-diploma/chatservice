from fastapi import HTTPException


class NotYourRequestException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Это обращение не принадлежит Вам!",
        )


class RequestAlreadyClosedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Данное обращение уже закрыто!",
        )
