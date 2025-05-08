from app.controllers.auth.dto import AccessJWTPayloadDto
from app.acl.permissions import PermissionAcl
from typing import Protocol
from fastapi import WebSocket
from pydantic import BaseModel


class IWebsocketController(Protocol):
    async def register_connect(
        self, user_dto: AccessJWTPayloadDto, connection: WebSocket
    ): ...
    async def register_disconnect(self, user_id: int): ...
    def is_connected(self, user_id: int): ...
    async def send_payload(self, user_id: int, dto: BaseModel): ...
    async def broadcast_to_privileged(
        self, acl: PermissionAcl, dto: BaseModel
    ): ...
