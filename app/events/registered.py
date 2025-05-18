# костыль, но pyee не умеет работать с методами

from app.dependencies import get_request_service, get_websocket_manager
from app.events.emitter import Emitter, Events, ExternalEvents
from app.services.requests.dto import MessageDto, RequestDto
from app.acl.permissions import Permissions

from app.services.ws.dto import (
    RequestClosedWsOutDto,
    RequestOpenedWsOutDto,
    MessageWsOutDto,
)


@Emitter.on(Events.Message)
async def on_message(message: MessageDto):
    ws_manager = get_websocket_manager()
    ws_message = MessageWsOutDto(data=message)
    request_service = get_request_service()

    await ws_manager.broadcast_to_privileged(
        Permissions.GetAllRequests, ws_message, {message.user_id}
    )

    request = await request_service.get_request(message.request_id)
    if request.author_user_id != message.user_id and ws_manager.is_connected(
        request.author_user_id
    ):
        await ws_manager.send_payload(request.author_user_id, ws_message)


@Emitter.on(Events.RequestOpened)
async def on_request_opened(request_dto: RequestDto):
    ws_manager = get_websocket_manager()
    ws_message = RequestOpenedWsOutDto(data=request_dto)

    await ws_manager.broadcast_to_privileged(
        Permissions.GetAllRequests, ws_message, {request_dto.author_user_id}
    )


@Emitter.on(Events.RequestClosed)
async def on_request_closed(request_dto: RequestDto):
    ws_manager = get_websocket_manager()
    ws_message = RequestClosedWsOutDto(data=request_dto)

    await ws_manager.broadcast_to_privileged(
        Permissions.GetAllRequests,
        ws_message,
        {request_dto.closed_by_user_id or 0},
    )

    if (
        request_dto.closed_by_user_id != request_dto.author_user_id
        and ws_manager.is_connected(request_dto.author_user_id)
    ):
        await ws_manager.send_payload(request_dto.author_user_id, ws_message)


@Emitter.on(ExternalEvents.HackathonDeleted)
async def on_hackathon_deleted(payload: dict):
    hackathon_id = payload["data"]["id"]
    request_service = get_request_service()
    await request_service.delete_by_hackathon(hackathon_id)


@Emitter.on(ExternalEvents.UserDeleted)
async def on_user_deleted(payload: dict):
    user_id = payload["data"]["id"]
    request_service = get_request_service()
    await request_service.delete_by_user(user_id)
