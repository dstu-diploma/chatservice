from app.acl.permissions import Permissions, perform_check
from app.controllers.auth.dto import AccessJWTPayloadDto
from app.controllers.auth import PermittedAction, get_user_dto
from fastapi import APIRouter, Depends

from app.controllers.auth.exceptions import RestrictedPermissionException
from app.controllers.requests.interfaces import IRequestController
from app.controllers.requests import get_request_controller
from app.controllers.requests.dto import MessageDto, RequestDto
from app.views.root.dto import (
    CreateRequestDto,
    RequestSendMessageDto,
    RequestWithMessagesDto,
)
from app.views.root.exceptions import (
    NotYourRequestException,
    RequestAlreadyClosedException,
)


router = APIRouter(tags=["Основное"], prefix="")


@router.get("/", response_model=list[RequestDto], summary="Список обращений")
async def get_requests(
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    controller: IRequestController = Depends(get_request_controller),
):
    """
    Возвращает список всех обращений текущего пользователя.
    Если текущий пользователь - привилегированное лицо (хелпер, организатор или админ), то
    возвращает список всех обращений.
    """
    if perform_check(Permissions.GetAllRequests, user_dto.role):
        return await controller.get_all_requests()
    elif perform_check(Permissions.GetSelfRequests, user_dto.role):
        return await controller.get_requests_by_user(user_dto.user_id)

    raise RestrictedPermissionException()


@router.get(
    "/{request_id}",
    response_model=RequestWithMessagesDto,
    summary="Получить информацию об обращении",
)
async def get_request_by_id(
    request_id: int,
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    controller: IRequestController = Depends(get_request_controller),
):
    """
    Возвращает полную информацию об обращении, включая список сообщений.
    Привилегированное лицо имеет право получать информацию о любом обращении.
    """
    can_view_own = perform_check(Permissions.GetSelfRequests, user_dto.role)
    can_view_all = perform_check(Permissions.GetAllRequests, user_dto.role)

    if not can_view_own and not can_view_all:
        raise RestrictedPermissionException()

    request = await controller.get_request(request_id)
    if request.author_user_id != user_dto.user_id and not can_view_all:
        raise NotYourRequestException()

    messages = await controller.get_request_history(request_id)

    return RequestWithMessagesDto(messages=messages, **request.model_dump())


@router.put(
    "/", response_model=RequestWithMessagesDto, summary="Создать обращение"
)
async def create_request(
    dto: CreateRequestDto,
    user_dto: AccessJWTPayloadDto = Depends(
        PermittedAction(Permissions.CreateRequest)
    ),
    controller: IRequestController = Depends(get_request_controller),
):
    """
    Регистрирует новое обращение.
    """
    request = await controller.create(
        user_dto.user_id, dto.subject, dto.message
    )
    messages = await controller.get_request_history(request.id)

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
    controller: IRequestController = Depends(get_request_controller),
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

    request = await controller.get_request(request_id)
    if request.author_user_id != user_dto.user_id and not can_post_all:
        raise NotYourRequestException()

    return await controller.send_message(
        request_id, user_dto.user_id, dto.message
    )


@router.delete(
    "/{request_id}", response_model=RequestDto, summary="Закрытие обращения"
)
async def close_request(
    request_id: int,
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    controller: IRequestController = Depends(get_request_controller),
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

    request = await controller.get_request(request_id)
    if not await controller.is_request_open(request_id):
        raise RequestAlreadyClosedException()

    if request.author_user_id != user_dto.user_id and not can_close_all:
        raise NotYourRequestException()

    return await controller.close_request(request_id, user_dto.user_id)
