from fastapi import APIRouter, Depends

from app.controllers.auth import get_user_dto
from app.controllers.auth.dto import AccessJWTPayloadDto
from app.controllers.message import MessageController
from app.controllers.message.dto import ChatMessageDto

router = APIRouter(tags=["Основное"], prefix="")


@router.get("/", response_model=list[int], summary="Получение списка чатов")
async def get_chats(
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    controller: MessageController = Depends(),
):
    """
    Возвращает список ID пользователей, с которыми текущий залогиненный пользователь хотя бы раз общался.
    ID отсортированы по дате последнего сообщения.
    """
    return await controller.get_user_chats(user_dto.user_id)


@router.get(
    "/history/{id}",
    response_model=list[ChatMessageDto],
    summary="Получение истории сообщений",
)
async def get_chat_history(
    id: int,
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    controller: MessageController = Depends(),
):
    """
    Возвращает историю общения с пользователем.
    Все сообщения отсортированы в порядке отправления (чем позже отправлено сообщение, тем ближе к концу списка).
    """
    return await controller.get_for_users(user_dto.user_id, id)
