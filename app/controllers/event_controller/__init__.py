from pyee.asyncio import AsyncIOEventEmitter
from enum import StrEnum


class Events(StrEnum):
    Message = "message"
    RequestOpened = "request_opened"
    RequestClosed = "request_closed"


Emitter = AsyncIOEventEmitter()
