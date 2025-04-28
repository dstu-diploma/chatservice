from pydantic import BaseModel
from datetime import datetime

from app.models.chat import ChatMessageModel


class ChatMessageDto(BaseModel):
    id: int
    from_user_id: int
    to_user_id: int
    contents: str

    send_time: datetime
    read_time: datetime | None = None

    @staticmethod
    def from_tortoise(message: ChatMessageModel):
        return ChatMessageDto(
            id=message.id,
            from_user_id=message.from_user_id,
            to_user_id=message.to_user_id,
            contents=message.contents,
            send_time=message.send_time,
            read_time=message.read_time,
        )
