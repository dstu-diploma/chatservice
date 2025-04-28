from pydantic import BaseModel


class WsMessageDto(BaseModel):
    action: str
    user_id: int
