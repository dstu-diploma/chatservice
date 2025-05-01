from app.controllers.user import IUserController, get_user_controller
from app.controllers.message.interfaces import IMessageController
from app.controllers.event_controller import Emitter, Events
from app.controllers.message.dto import ChatMessageDto
from chatservice.app.controllers.user.exceptions import (
    UserDoesNotExistException,
)
from .exceptions import NoSuchMessageException
from app.models.chat import ChatMessageModel
from tortoise.expressions import Q, F
from tortoise.functions import Max
from functools import lru_cache
from datetime import datetime
from fastapi import Depends
import typing


class MessageController(IMessageController):
    user_controller: IUserController

    def __init__(self, user_controller: IUserController):
        self.user_controller = user_controller

    async def has_chat(self, from_user_id: int, to_user_id: int) -> bool:
        return await ChatMessageModel.exists(
            from_user_id=from_user_id, to_user_id=to_user_id
        )

    async def create(
        self, from_user_id: int, to_user_id: int, contents: str
    ) -> ChatMessageDto:
        if not await self.has_chat(
            from_user_id, to_user_id
        ) and not await self.user_controller.get_user_exists(to_user_id):
            raise UserDoesNotExistException()

        message = await ChatMessageModel.create(
            from_user_id=from_user_id, to_user_id=to_user_id, contents=contents
        )

        dto = ChatMessageDto.from_tortoise(message)
        Emitter.emit(Events.Message, dto)

        return dto

    async def _get_by_id(self, message_id: int) -> ChatMessageModel:
        message = await ChatMessageModel.get_or_none(id=message_id)
        if message is None:
            raise NoSuchMessageException()

        return message

    async def get_by_id(self, message_id: int) -> ChatMessageDto:
        return ChatMessageDto.from_tortoise(await self._get_by_id(message_id))

    async def delete(self, message_id: int) -> None:
        message = await self._get_by_id(message_id)
        await message.delete()

    async def get_for_users(
        self, from_user_id: int, to_user_id: int
    ) -> list[ChatMessageDto]:
        messages = await ChatMessageModel.filter(
            from_user_id=from_user_id, to_user_id=to_user_id
        )
        return [ChatMessageDto.from_tortoise(message) for message in messages]

    async def get_user_chats(self, user_id: int) -> list[int]:
        # ниггер слаб в резолве типов
        partner_times = typing.cast(
            list[int],
            await ChatMessageModel.filter(
                Q(from_user_id=user_id) | Q(to_user_id=user_id)
            )
            .annotate(
                partner_id=(
                    F("to_user_id")
                    if F("from_user_id") == user_id
                    else F("from_user_id")
                )
            )
            .group_by("partner_id")
            .annotate(last_time=Max("send_time"))
            .order_by("last_time")
            .values_list("partner_id", flat=True),
        )

        return partner_times

    async def mark_readed(self, message_id: int) -> ChatMessageDto:
        message = await self._get_by_id(message_id)
        message.read_time = datetime.now()
        await message.save()
        return ChatMessageDto.from_tortoise(message)


@lru_cache
def get_message_controller(
    user_controller: IUserController = Depends(get_user_controller),
) -> MessageController:
    return MessageController(user_controller)
