from fastapi import HTTPException


class NotYourMessageException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Вы не можете удалить чужое сообщение!",
        )
