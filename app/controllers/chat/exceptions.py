from fastapi import HTTPException


class NoSuchMessageException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Сообщения с таким ID не существует!",
        )
