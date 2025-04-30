from pydantic import BaseModel

from app.controllers.message.dto import ChatMessageDto


class StatusDto(BaseModel):
    user_id: int
    is_online: bool


class BaseWsOutDto(BaseModel):
    action: str


class MessageWsOutDto(BaseWsOutDto):
    action: str = "message"
    data: ChatMessageDto


class StatusWsOutDto(BaseWsOutDto):
    action: str = "status"
    data: StatusDto
