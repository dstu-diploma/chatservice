from app.acl.permissions import PermissionAcl, Permissions, perform_check
from app.controllers.requests.dto import MessageDto, RequestDto
from app.controllers.event_controller import Emitter, Events
from app.controllers.requests import get_request_controller
from app.controllers.auth.dto import AccessJWTPayloadDto
from app.acl.roles import UserRoles
from functools import lru_cache
from pydantic import BaseModel
from fastapi import WebSocket
import asyncio

from app.controllers.ws.dto import (
    MessageWsOutDto,
    RequestClosedWsOutDto,
    RequestOpenedWsOutDto,
)


class WebsocketController:
    _connections: dict[int, WebSocket]

    def __init__(self):
        self._connections = {}

    async def register_connect(
        self, user_dto: AccessJWTPayloadDto, connection: WebSocket
    ):
        user_id = user_dto.user_id
        self._connections[user_id] = connection
        connection.scope["user_id"] = user_id
        connection.scope["role"] = user_dto.role

    async def register_disconnect(self, user_id: int):
        del self._connections[user_id]

    def is_connected(self, user_id: int):
        return user_id in self._connections

    async def send_payload(self, user_id: int, dto: BaseModel):
        user = self._connections[user_id]
        payload = dto.model_dump_json()

        await user.send_text(payload)

    async def broadcast_to_privileged(
        self, acl: PermissionAcl, dto: BaseModel, ignore_user_ids: set[int]
    ):
        awaitables = []

        for user_id in self._connections:
            if user_id in ignore_user_ids:
                continue

            user = self._connections[user_id]
            role = user.scope.get("role", UserRoles.User)

            if not perform_check(acl, role):
                continue

            awaitables.append(self.send_payload(user_id, dto))

        await asyncio.gather(*awaitables)


@lru_cache
def get_websocket_controller() -> WebsocketController:
    return WebsocketController()


# костыль, но pyee не умеет работать с методами
@Emitter.on(Events.Message)
async def __on_message(message: MessageDto):
    ws_controller = get_websocket_controller()
    request_controller = get_request_controller()

    ws_message = MessageWsOutDto(data=message)

    await ws_controller.broadcast_to_privileged(
        Permissions.GetAllRequests, ws_message, {message.user_id}
    )

    request = await request_controller.get_request(message.request_id)
    if (
        request.author_user_id != message.user_id
        and ws_controller.is_connected(request.author_user_id)
    ):
        await ws_controller.send_payload(request.author_user_id, ws_message)


@Emitter.on(Events.RequestOpened)
async def __on_request_opened(request_dto: RequestDto):
    ws_controller = get_websocket_controller()

    ws_message = RequestOpenedWsOutDto(data=request_dto)

    await ws_controller.broadcast_to_privileged(
        Permissions.GetAllRequests, ws_message, {request_dto.author_user_id}
    )


@Emitter.on(Events.RequestClosed)
async def __on_request_closed(request_dto: RequestDto):
    ws_controller = get_websocket_controller()

    ws_message = RequestClosedWsOutDto(data=request_dto)

    await ws_controller.broadcast_to_privileged(
        Permissions.GetAllRequests,
        ws_message,
        {request_dto.closed_by_user_id or 0},
    )

    if (
        request_dto.closed_by_user_id != request_dto.author_user_id
        and ws_controller.is_connected(request_dto.author_user_id)
    ):
        await ws_controller.send_payload(request_dto.author_user_id, ws_message)
