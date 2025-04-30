from pydantic import BaseModel


class WsBaseHandlerInDto(BaseModel):
    pass


class WsBaseHandlerOutDto(BaseModel):
    action: str
    data: BaseModel
