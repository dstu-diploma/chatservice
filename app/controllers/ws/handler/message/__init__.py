from app.controllers.message.dto import ChatMessageDto
from app.controllers.message.interfaces import IMessageController
from app.controllers.ws.handler.registry import register_handler
from app.controllers.ws.interfaces import IWebsocketController
from app.controllers.ws.handler.dto import (
    WsBaseHandlerInDto,
    WsBaseHandlerOutDto,
)


class WsMessageHandlerInDto(WsBaseHandlerInDto):
    to_user_id: int
    message: str


class WsMessageHandlerOutDto(WsBaseHandlerOutDto):
    action: str = "message"
    data: ChatMessageDto


@register_handler("message", WsMessageHandlerInDto)
async def test(
    user_id: int,
    ws_controller: IWebsocketController,
    dto: WsMessageHandlerInDto,
    message_controller: IMessageController,
):
    sent_message = await message_controller.create(
        user_id, dto.to_user_id, dto.message
    )

    if ws_controller.is_connected(dto.to_user_id):
        await ws_controller.send_payload(
            dto.to_user_id, WsMessageHandlerOutDto(data=sent_message)
        )
