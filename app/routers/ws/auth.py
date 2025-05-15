from app.services.auth import get_user_dto_from_token
from app.routers.ws.dto import WsMessageDto
from app.routers.ws.exception import (
    NoActionProvidenException,
    NoAuthTokenProvidenException,
)


def get_message_header(payload: dict[str, str]) -> WsMessageDto:
    if "action" not in payload:
        raise NoActionProvidenException()

    if "token" not in payload:
        raise NoAuthTokenProvidenException()

    user_dto = get_user_dto_from_token(payload["token"])
    return WsMessageDto(action=payload["action"], user_id=user_dto.user_id)
