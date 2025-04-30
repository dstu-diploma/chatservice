from app.controllers.event_controller import Emitter, Events
from app.controllers.message.dto import ChatMessageDto
from app.controllers.message.interfaces import IMessageController
from app.controllers.ws.interfaces import IWebsocketController
from app.controllers.ws.dto import MessageWsOutDto, StatusDto, StatusWsOutDto
from app.controllers.message import get_message_controller
from functools import lru_cache
from pydantic import BaseModel
from fastapi import WebSocket


def generate_online_status(user_id: int, is_online: bool):
    return StatusWsOutDto(data=StatusDto(user_id=user_id, is_online=is_online))


class WebsocketController(IWebsocketController):
    _connections: dict[int, WebSocket]
    _message_controller: IMessageController

    def __init__(self, message_controller: IMessageController):
        self._connections = {}
        self._message_controller = message_controller

    async def register_connect(self, user_id: int, connection: WebSocket):
        # отправляем уведомление до регистрации коннекта для того, чтобы только что законнекченому пользователю
        # не пришло сообщение
        await self.broadcast_payload(
            generate_online_status(user_id, is_online=True)
        )

        self._connections[user_id] = connection
        connection.scope["user_id"] = user_id

        Emitter.emit(Events.UserOnline, user_id)

    async def register_disconnect(self, user_id: int):
        del self._connections[user_id]

        await self.broadcast_payload(
            generate_online_status(user_id, is_online=False)
        )

        Emitter.emit(Events.UserOffline, user_id)

    def is_connected(self, user_id: int):
        return user_id in self._connections

    async def send_payload(self, user_id: int, dto: BaseModel):
        user = self._connections[user_id]
        payload = dto.model_dump_json()

        await user.send_text(payload)

    async def broadcast_payload(self, dto: BaseModel):
        payload = dto.model_dump_json()

        for user in self._connections.values():
            await user.send_text(payload)


@lru_cache
def get_websocket_controller() -> WebsocketController:
    return WebsocketController(get_message_controller())


# костыль, но pyee не умеет работать с методами
@Emitter.on(Events.Message)
async def __on_message(message: ChatMessageDto):
    controller = get_websocket_controller()
    if controller.is_connected(message.to_user_id):
        await controller.send_payload(
            message.to_user_id, MessageWsOutDto(data=message)
        )
