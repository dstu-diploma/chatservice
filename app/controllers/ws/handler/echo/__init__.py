from app.controllers.message.interfaces import IMessageController
from app.controllers.ws.handler.registry import register_handler
from app.controllers.ws.interfaces import IWebsocketController
from app.controllers.ws.handler.dto import (
    WsBaseHandlerInDto,
    WsBaseHandlerOutDto,
)


class WsEchoHandlerOutDto(WsBaseHandlerOutDto):
    action: str = "echo"
    data: dict[str, None] = {}


@register_handler("echo", WsBaseHandlerInDto)
async def test(
    user_id: int,
    ws_controller: IWebsocketController,
    dto: WsBaseHandlerInDto,
    message_controller: IMessageController,
):
    await ws_controller.send_payload(user_id, WsEchoHandlerOutDto())
