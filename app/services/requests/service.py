from app.ports.hackathonservice import IHackathonServicePort
from app.services.requests.interfaces import IRequestService
from app.models.chat import RequestModel, MessageModel
from app.ports.userservice import IUserServicePort
from tortoise.transactions import in_transaction
from app.events.emitter import Emitter, Events
from .dto import MessageDto, RequestDto
from app.util import dto_utils

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

    async def _inject_names(self, dtos: list[RequestDto]) -> list[RequestDto]:
        user_names = self.user_service.get_name_map(
            await self.user_service.try_get_user_info_many(
                dto_utils.export_int_fields(
                    dtos, "author_user_id", "closed_by_user_id"
                )
            )
        )

        hackathon_names = self.hackathon_service.get_name_map(
            await self.hackathon_service.try_get_hackathon_data_many(
                dto_utils.export_int_fields(dtos, "hackathon_id")
            )
        )

        dtos = dto_utils.inject_mapping(
            dtos, user_names, "_user_id", "_name", strict=False
        )
        dtos = dto_utils.inject_mapping(
            dtos,
            hackathon_names,
            "hackathon_id",
            "hackathon_name",
            strict=True,
        )

        return dtos

    async def get_all_requests(self) -> list[RequestDto]:
        dtos = [
            RequestDto.from_tortoise(request)
            for request in await RequestModel.all()
        ]

        return await self._inject_names(dtos)

    async def get_requests_by_user(self, user_id: int) -> list[RequestDto]:
        return await self._inject_names(
            [
                RequestDto.from_tortoise(request)
                for request in await RequestModel.filter(author_user_id=user_id)
            ]
        )

    async def _get_request(self, request_id: int) -> RequestModel:
        request = await RequestModel.get_or_none(id=request_id)
        if request is None:
            raise NoSuchRequestException()

        return request

    async def get_request(self, request_id: int) -> RequestDto:
        dtos = await self._inject_names(
            [RequestDto.from_tortoise(await self._get_request(request_id))]
        )

        return dtos[0]

    async def get_request_history(self, request_id: int) -> list[MessageDto]:
        await self._get_request(request_id)
        dtos = [
            MessageDto.from_tortoise(message)
            for message in await MessageModel.filter(request_id=request_id)
        ]

        user_names = self.user_service.get_name_map(
            await self.user_service.try_get_user_info_many(
                dto_utils.export_int_fields(dtos, "user_id")
            )
        )

        return dto_utils.inject_mapping(
            dtos, user_names, "user_id", "user_name", strict=True
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
            request_dto.author_name = user_info.formatted_name

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
            message_dto.user_name = user_info.formatted_name

        Emitter.emit(Events.Message, message_dto)
        return message_dto
