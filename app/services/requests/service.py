from app.ports.hackathonservice import IHackathonServicePort
from app.services.requests.interfaces import IRequestService
from app.services.event_controller import Emitter, Events
from app.models.chat import RequestModel, MessageModel
from app.ports.userservice import IUserServicePort
from tortoise.transactions import in_transaction
from .dto import MessageDto, RequestDto
from collections import defaultdict

from .exceptions import (
    CantSendMessagesRequestIsClosedException,
    NoSuchRequestException,
)


class RequestService(IRequestService):
    def __init__(
        self,
        user_service: IUserServicePort,
        hackathon_service: IHackathonServicePort,
    ):
        self.user_service = user_service
        self.hackathon_service = hackathon_service

    def _get_request_user_ids(
        self, requests: list[RequestDto]
    ) -> frozenset[int]:
        return frozenset(
            request.author_user_id for request in requests
        ) | frozenset(
            request.closed_by_user_id
            for request in requests
            if request.closed_by_user_id
        )

    def _get_message_user_ids(
        self, messages: list[MessageDto]
    ) -> frozenset[int]:
        return frozenset(message.user_id for message in messages)

    def _inject_request_names(
        self, dtos: list[RequestDto], names: defaultdict[int, str | None]
    ):
        for dto in dtos:
            dto.author_name = names[dto.author_user_id]

            if dto.closed_by_user_id:
                dto.closed_by_name = names[dto.closed_by_user_id]

    def _inject_message_names(
        self, dtos: list[MessageDto], names: defaultdict[int, str | None]
    ):
        for dto in dtos:
            dto.user_name = names[dto.user_id]

    async def _request_models_to_dtos(
        self, instances: list[RequestModel]
    ) -> list[RequestDto]:
        dtos = [RequestDto.from_tortoise(request) for request in instances]
        names = self.user_service.get_name_map(
            await self.user_service.try_get_user_info_many(
                self._get_request_user_ids(dtos)
            )
        )
        self._inject_request_names(dtos, names)
        return dtos

    async def _message_models_to_dtos(
        self, instances: list[MessageModel]
    ) -> list[MessageDto]:
        dtos = [MessageDto.from_tortoise(message) for message in instances]
        names = self.user_service.get_name_map(
            await self.user_service.try_get_user_info_many(
                self._get_message_user_ids(dtos)
            )
        )

        self._inject_message_names(dtos, names)
        return dtos

    async def get_all_requests(self) -> list[RequestDto]:
        return await self._request_models_to_dtos(await RequestModel.all())

    async def get_requests_by_user(self, user_id: int) -> list[RequestDto]:
        return await self._request_models_to_dtos(
            await RequestModel.filter(author_user_id=user_id)
        )

    async def _get_request(self, request_id: int) -> RequestModel:
        request = await RequestModel.get_or_none(id=request_id)
        if request is None:
            raise NoSuchRequestException()

        return request

    async def get_request(self, request_id: int) -> RequestDto:
        dtos = await self._request_models_to_dtos(
            [await self._get_request(request_id)]
        )

        return dtos[0]

    async def get_request_history(self, request_id: int) -> list[MessageDto]:
        await self._get_request(request_id)
        return await self._message_models_to_dtos(
            await MessageModel.filter(request_id=request_id)
        )

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
        self,
        hackathon_id: int,
        author_user_id: int,
        subject: str,
        first_message: str,
    ) -> RequestDto:
        hackathon_info = await self.hackathon_service.get_hackathon_data(
            hackathon_id
        )

        async with in_transaction():
            request = await RequestModel.create(
                author_user_id=author_user_id,
                subject=subject,
                hackathon_id=hackathon_id,
            )

            await self.send_message(request.id, author_user_id, first_message)

        request_dto = RequestDto.from_tortoise(request)
        request_dto.hackathon_name = hackathon_info.name

        user_info = await self.user_service.try_get_user_info(author_user_id)
        if user_info:
            request_dto.author_name = self.user_service.format_name(user_info)

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
        user_info = await self.user_service.try_get_user_info(user_id)
        if user_info:
            message_dto.user_name = self.user_service.format_name(user_info)

        Emitter.emit(Events.Message, message_dto)
        return message_dto
