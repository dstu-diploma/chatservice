from typing import Annotated
from pydantic import BaseModel, StringConstraints
from app.services.requests.dto import MessageDto, RequestDto


class RequestWithMessagesDto(RequestDto):
    messages: list[MessageDto]


class RequestSendMessageDto(BaseModel):
    message: Annotated[str, StringConstraints(min_length=3, max_length=500)]


class CreateRequestDto(RequestSendMessageDto):
    subject: Annotated[str, StringConstraints(min_length=3, max_length=150)]
