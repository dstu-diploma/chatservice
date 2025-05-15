from app.acl.permissions import PermissionAcl, perform_check
from app.services.ws.interfaces import IWebsocketManager
from app.services.auth.dto import AccessJWTPayloadDto
from app.acl.roles import UserRoles
from pydantic import BaseModel
from fastapi import WebSocket
import asyncio


class WebsocketManager(IWebsocketManager):
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

    def is_connected(self, user_id: int) -> bool:
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
