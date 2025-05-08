from app.controllers.requests.dto import MessageDto, RequestDto
from pydantic import BaseModel


class BaseWsOutDto(BaseModel):
    action: str


class MessageWsOutDto(BaseWsOutDto):
    action: str = "message"
    data: MessageDto


class RequestOpenedWsOutDto(BaseWsOutDto):
    action: str = "request_opened"
    data: RequestDto


class RequestClosedWsOutDto(BaseWsOutDto):
    action: str = "request_closed"
    data: RequestDto
