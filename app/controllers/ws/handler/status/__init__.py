from pydantic import BaseModel
from app.controllers.ws.handler.dto import WsBaseHandlerOutDto


class OnlineStatusDto(BaseModel):
    user_id: int
    online: bool


class WsMessageHandlerOutDto(WsBaseHandlerOutDto):
    action: str = "online"
    data: OnlineStatusDto


def generate_online_status(
    user_id: int, online: bool
) -> WsMessageHandlerOutDto:
    return WsMessageHandlerOutDto(
        data=OnlineStatusDto(user_id=user_id, online=online)
    )
