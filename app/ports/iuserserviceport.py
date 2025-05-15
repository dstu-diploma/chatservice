from typing import Protocol


class IUserServicePort(Protocol):
    async def get_user_exists(self, user_id: int) -> bool: ...
