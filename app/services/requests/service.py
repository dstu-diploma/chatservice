from app.services.requests.interfaces import IRequestService
from app.services.event_controller import Emitter, Events
from app.models.chat import RequestModel, MessageModel
from tortoise.transactions import in_transaction
from .dto import MessageDto, RequestDto
from functools import lru_cache

from .exceptions import (
    CantSendMessagesRequestIsClosedException,
    NoSuchRequestException,
)


class RequestService(IRequestService):
    async def get_all_requests(self) -> list[RequestDto]:
        requests = await RequestModel.all()
        return [RequestDto.from_tortoise(request) for request in requests]

    async def get_requests_by_user(self, user_id: int) -> list[RequestDto]:
        requests = await RequestModel.filter(author_user_id=user_id)
        return [RequestDto.from_tortoise(request) for request in requests]

    async def _get_request(self, request_id: int) -> RequestModel:
        request = await RequestModel.get_or_none(id=request_id)
        if request is None:
            raise NoSuchRequestException()

        return request

    async def get_request(self, request_id: int) -> RequestDto:
        return RequestDto.from_tortoise(await self._get_request(request_id))

    async def get_request_history(self, request_id: int) -> list[MessageDto]:
        await self._get_request(request_id)

        messages = await MessageModel.filter(request_id=request_id)
        return [MessageDto.from_tortoise(message) for message in messages]

    async def is_request_open(self, request_id: int) -> bool:
        request = await self._get_request(request_id)
        return request.closed_by_user_id is None

    async def close_request(
        self, request_id: int, closed_by_user_id: int
    ) -> RequestDto:
        request = await self._get_request(request_id)

        if request.closed_by_user_id is None:
            request.closed_by_user_id = closed_by_user_id
            await request.save()

        request_dto = RequestDto.from_tortoise(request)
        Emitter.emit(Events.RequestClosed, request_dto)
        return request_dto

    async def create(
        self, author_user_id: int, subject: str, first_message: str
    ) -> RequestDto:
        async with in_transaction():
            request = await RequestModel.create(
                author_user_id=author_user_id, subject=subject
            )

            await self.send_message(request.id, author_user_id, first_message)

        request_dto = RequestDto.from_tortoise(request)
        Emitter.emit(Events.RequestOpened, request_dto)
        return request_dto

    async def send_message(
        self, request_id: int, user_id: int, message: str
    ) -> MessageDto:
        if not await self.is_request_open(request_id):
            raise CantSendMessagesRequestIsClosedException()

        message_obj = await MessageModel.create(
            user_id=user_id, message=message, request_id=request_id
        )

        message_dto = MessageDto.from_tortoise(message_obj)
        Emitter.emit(Events.Message, message_dto)

        return message_dto
