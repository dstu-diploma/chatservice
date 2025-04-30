from pydantic import BaseModel


class SendMessageDto(BaseModel):
    to_user_id: int
    contents: str
