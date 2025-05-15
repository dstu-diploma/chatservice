from app.ports.userservice.dto import MinimalUserDto
from typing import Protocol


class IUserServicePort(Protocol):
    base_url: str

    async def get_user_info(self, user_id: int) -> MinimalUserDto: ...
    async def try_get_user_info(
        self, user_id: int
    ) -> MinimalUserDto | None: ...
