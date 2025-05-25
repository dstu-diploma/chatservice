from fastapi import HTTPException


class NoSuchRequestException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Обращения с таким ID не существует!",
        )


class NoAccessToRequestException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Вы не имееет права взаимодействовать с данным обращением!",
        )


class CantSendMessagesRequestIsClosedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Данное обращение закрыто!",
        )
