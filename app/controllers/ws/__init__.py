from app.controllers.message import MessageController
from app.controllers.message.interfaces import IMessageController
from app.controllers.ws.handler.registry import REGISTERED_HANDLERS
from app.controllers.ws.interfaces import IWebsocketController
from pydantic import BaseModel, ValidationError
from fastapi import WebSocket
from typing import Any

from app.controllers.ws.exceptions import (
    ActionValidationPayloadException,
    NoSuchActionException,
)


class WebsocketController(IWebsocketController):
    _connections: dict[int, WebSocket]
    _message_controller: IMessageController

    def __init__(self, message_controller: IMessageController):
        self._connections = {}
        self._message_controller = message_controller

    def register_connect(self, user_id: int, connection: WebSocket):
        self._connections[user_id] = connection
        connection.scope["user_id"] = user_id

    def register_disconnect(self, user_id: int):
        del self._connections[user_id]

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

    async def run_action(
        self, user_id: int, action_name: str, action_data: dict[str, Any]
    ):
        if action_name not in REGISTERED_HANDLERS:
            raise NoSuchActionException()

        DtoModel, handler = REGISTERED_HANDLERS[action_name]
        try:
            validated_data = DtoModel.model_validate(action_data)
            await handler(
                user_id, self, validated_data, self._message_controller
            )
        except ValidationError:
            raise ActionValidationPayloadException()


# свэг
__controller = WebsocketController(MessageController())


def get_websocket_controller() -> WebsocketController:
    return __controller
