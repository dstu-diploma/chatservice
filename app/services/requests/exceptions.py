from fastapi import HTTPException


class NoSuchRequestException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Обращения с таким ID не существует!",
        )


class CantSendMessagesRequestIsClosedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Данное обращение закрыто!",
        )
