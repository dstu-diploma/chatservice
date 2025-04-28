from app.controllers.chat.dto import ChatMessageDto
from .exceptions import NoSuchMessageException
from app.models.chat import ChatMessageModel
from datetime import datetime


class MessageController:
    def __init__(self):
        pass

    async def create(
        self, from_user_id: int, to_user_id: int, contents: str
    ) -> ChatMessageDto:
        message = await ChatMessageModel.create(
            from_user_id=from_user_id, to_user_id=to_user_id, contents=contents
        )

        return ChatMessageDto.from_tortoise(message)

    async def _get_by_id(self, message_id: int) -> ChatMessageModel:
        message = await ChatMessageModel.get_or_none(id=message_id)
        if message is None:
            raise NoSuchMessageException()

        return message

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

    async def mark_readed(self, message_id: int) -> ChatMessageDto:
        message = await self._get_by_id(message_id)
        message.read_time = datetime.now()
        await message.save()
        return ChatMessageDto.from_tortoise(message)
