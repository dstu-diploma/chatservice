from pyee.asyncio import AsyncIOEventEmitter
from enum import StrEnum


class Events(StrEnum):
    Message = "message"
    UserOnline = "user_online"
    UserOffline = "user_offline"


Emitter = AsyncIOEventEmitter()
