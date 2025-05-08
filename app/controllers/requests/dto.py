from app.models.chat import MessageModel, RequestModel
from datetime import datetime
from pydantic import BaseModel


class RequestDto(BaseModel):
    id: int
    author_user_id: int
    subject: str
    closed_by_user_id: int | None

    @staticmethod
    def from_tortoise(request: RequestModel):
        return RequestDto(
            id=request.id,
            author_user_id=request.author_user_id,
            subject=request.subject,
            closed_by_user_id=request.closed_by_user_id,
        )


class MessageDto(BaseModel):
    id: int
    user_id: int
    message: str
    request_id: int
    send_date: datetime

    @staticmethod
    def from_tortoise(message: MessageModel):
        return MessageDto(
            id=message.id,
            user_id=message.user_id,
            message=message.message,
            request_id=message.request_id,  # type: ignore[attr-defined]
            send_date=message.send_date,
        )
