from pydantic import BaseModel
from app.controllers.ws.handler.dto import WsBaseHandlerOutDto


class OnlineStatusDto(BaseModel):
    user_id: int
    online: bool


class WsStatusHandlerOutDto(WsBaseHandlerOutDto):
    action: str = "online"
    data: OnlineStatusDto


def generate_online_status(user_id: int, online: bool) -> WsStatusHandlerOutDto:
    return WsStatusHandlerOutDto(
        data=OnlineStatusDto(user_id=user_id, online=online)
    )
