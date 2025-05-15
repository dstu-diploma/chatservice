from app.services.auth.exceptions import RestrictedPermissionException
from app.services.requests.interfaces import IRequestService
from app.services.requests.dto import MessageDto, RequestDto
from app.services.auth import PermittedAction, get_user_dto
from app.acl.permissions import Permissions, perform_check
from app.services.auth.dto import AccessJWTPayloadDto
from app.dependencies import get_request_service
from fastapi import APIRouter, Depends

from app.routers.root.dto import (
    RequestWithMessagesDto,
    RequestSendMessageDto,
    CreateRequestDto,
)
from app.routers.root.exceptions import (
    RequestAlreadyClosedException,
    NotYourRequestException,
)


router = APIRouter(tags=["Основное"], prefix="")


@router.get("/", response_model=list[RequestDto], summary="Список обращений")
async def get_requests(
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    service: IRequestService = Depends(get_request_service),
):
    """
    Возвращает список всех обращений текущего пользователя.
    Если текущий пользователь - привилегированное лицо (хелпер, организатор или админ), то
    возвращает список всех обращений.
    """
    if perform_check(Permissions.GetAllRequests, user_dto.role):
        return await service.get_all_requests()
    elif perform_check(Permissions.GetSelfRequests, user_dto.role):
        return await service.get_requests_by_user(user_dto.user_id)

    raise RestrictedPermissionException()


@router.get(
    "/{request_id}",
    response_model=RequestWithMessagesDto,
    summary="Получить информацию об обращении",
)
async def get_request_by_id(
    request_id: int,
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    service: IRequestService = Depends(get_request_service),
):
    """
    Возвращает полную информацию об обращении, включая список сообщений.
    Привилегированное лицо имеет право получать информацию о любом обращении.
    """
    can_view_own = perform_check(Permissions.GetSelfRequests, user_dto.role)
    can_view_all = perform_check(Permissions.GetAllRequests, user_dto.role)

    if not can_view_own and not can_view_all:
        raise RestrictedPermissionException()

    request = await service.get_request(request_id)
    if request.author_user_id != user_dto.user_id and not can_view_all:
        raise NotYourRequestException()

    messages = await service.get_request_history(request_id)

    return RequestWithMessagesDto(messages=messages, **request.model_dump())


@router.put(
    "/", response_model=RequestWithMessagesDto, summary="Создать обращение"
)
async def create_request(
    dto: CreateRequestDto,
    user_dto: AccessJWTPayloadDto = Depends(
        PermittedAction(Permissions.CreateRequest)
    ),
    service: IRequestService = Depends(get_request_service),
):
    """
    Регистрирует новое обращение.
    """
    request = await service.create(
        dto.hackathon_id, user_dto.user_id, dto.subject, dto.message
    )
    messages = await service.get_request_history(request.id)

    return RequestWithMessagesDto(messages=messages, **request.model_dump())


@router.put(
    "/{request_id}",
    response_model=MessageDto,
    summary="Написать сообщение в обращение",
)
async def send_message(
    request_id: int,
    dto: RequestSendMessageDto,
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    service: IRequestService = Depends(get_request_service),
):
    """
    Отправляет сообщение в обращение.
    Привилегированное лицо может писать в любое обращение.
    """
    can_post_own = perform_check(Permissions.CreateMessage, user_dto.role)
    can_post_all = perform_check(
        Permissions.CreateMessageAsSupport, user_dto.role
    )

    if not can_post_own and not can_post_all:
        raise RestrictedPermissionException()

    request = await service.get_request(request_id)
    if request.author_user_id != user_dto.user_id and not can_post_all:
        raise NotYourRequestException()

    return await service.send_message(request_id, user_dto.user_id, dto.message)


@router.delete(
    "/{request_id}", response_model=RequestDto, summary="Закрытие обращения"
)
async def close_request(
    request_id: int,
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    service: IRequestService = Depends(get_request_service),
):
    """
    Помечает обращение как закрытое. В сущности сохраняется ID пользователя, закрывшего обращение.
    Попытка повторного закрытия вернет 400.
    """
    can_close_own = perform_check(Permissions.CloseRequest, user_dto.role)
    can_close_all = perform_check(
        Permissions.CloseRequestAsSupport, user_dto.role
    )

    if not can_close_own and not can_close_all:
        raise RestrictedPermissionException()

    request = await service.get_request(request_id)
    if not await service.is_request_open(request_id):
        raise RequestAlreadyClosedException()

    if request.author_user_id != user_dto.user_id and not can_close_all:
        raise NotYourRequestException()

    return await service.close_request(request_id, user_dto.user_id)
