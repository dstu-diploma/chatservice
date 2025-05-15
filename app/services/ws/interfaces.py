from app.services.auth.dto import AccessJWTPayloadDto
from app.acl.permissions import PermissionAcl
from pydantic import BaseModel
from fastapi import WebSocket
from typing import Protocol


class IWebsocketManager(Protocol):
    async def register_connect(
        self, user_dto: AccessJWTPayloadDto, connection: WebSocket
    ): ...
    async def register_disconnect(self, user_id: int): ...
    def is_connected(self, user_id: int) -> bool: ...
    async def send_payload(self, user_id: int, dto: BaseModel): ...
    async def broadcast_to_privileged(
        self, acl: PermissionAcl, dto: BaseModel, ignore_user_ids: set[int]
    ): ...
