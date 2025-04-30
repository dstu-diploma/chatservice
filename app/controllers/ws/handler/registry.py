from app.controllers.message.interfaces import IMessageController
from app.controllers.ws.interfaces import IWebsocketController
from app.controllers.ws.handler.dto import WsBaseHandlerInDto
from typing import Awaitable, Callable, Type
from pydantic import BaseModel


HandlerType = Callable[
    [int, IWebsocketController, BaseModel, IMessageController], Awaitable[None]
]
REGISTERED_HANDLERS: dict[str, tuple[Type[BaseModel], HandlerType]] = {}


def register_handler(action: str, dto_type: Type[WsBaseHandlerInDto]):
    def decorator(handler: HandlerType):
        REGISTERED_HANDLERS[action] = (dto_type, handler)
        return handler

    return decorator
