from app.controllers.message.interfaces import IMessageController
from app.controllers.ws.handler.registry import register_handler
from app.controllers.ws.interfaces import IWebsocketController
from app.controllers.ws.handler.dto import WsBaseHandlerDto


class WsMessageHandlerDto(WsBaseHandlerDto):
    to_user_id: int
    message: str


@register_handler("message", WsMessageHandlerDto)
async def test(
    user_id: int,
    ws_controller: IWebsocketController,
    dto: WsMessageHandlerDto,
    message_controller: IMessageController,
):
    sent_message = await message_controller.create(
        user_id, dto.to_user_id, dto.message
    )

    if ws_controller.is_connected(dto.to_user_id):
        await ws_controller.send_payload(dto.to_user_id, sent_message)
