from app.controllers.message import MessageController, get_message_controller
from app.views.message.exceptions import NotYourMessageException
from app.controllers.auth.dto import AccessJWTPayloadDto
from app.controllers.message.dto import ChatMessageDto
from app.views.message.dto import SendMessageDto
from app.controllers.auth import get_user_dto
from fastapi import APIRouter, Depends


router = APIRouter(tags=["Сообщения"], prefix="/message")


@router.post("/", response_model=ChatMessageDto, summary="Написать сообщение")
async def write_message(
    dto: SendMessageDto,
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    controller: MessageController = Depends(get_message_controller),
):
    """
    Отправляет пользователю сообщение. Если получатель онлайн, то ему по вебсокету придет соответствующее уведомление.
    """
    return await controller.create(
        user_dto.user_id, dto.to_user_id, dto.contents
    )


@router.delete(
    "/{id}", response_model=ChatMessageDto, summary="Удаление сообщения"
)
async def delete_message(
    id: int,
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    controller: MessageController = Depends(get_message_controller),
):
    """
    Удаляет сообщение у обоих пользователей (точнее, вообще из базы данных).
    Если пользователю не принадлежит данное сообщение, то вернет Bad Request.
    """
    message = await controller.get_by_id(id)
    if message.from_user_id != user_dto.user_id:
        raise NotYourMessageException()

    await controller.delete(message.id)
    return message


@router.put(
    "/{id}/read", response_model=ChatMessageDto, summary="Прочитать сообщение"
)
async def read_message(
    id: int,
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    controller: MessageController = Depends(get_message_controller),
):
    """
    Помечает сообщение как прочитанное.
    Если пользователю не принадлежит данное сообщение, то вернет Bad Request.
    Если сообщение уже прочитано, то ничего не произойдет.
    """
    message = await controller.get_by_id(id)
    if message.from_user_id != user_dto.user_id:
        raise NotYourMessageException()

    if message.read_time is not None:
        return message

    return await controller.mark_readed(id)
