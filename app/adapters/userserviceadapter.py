from app.ports.iuserserviceport import IUserServicePort
from .exceptions import UserServiceError
from functools import lru_cache
from fastapi import Depends
from os import environ
import httpx

USER_SERVICE_URL = environ.get("USER_SERVICE_URL")
USER_SERVICE_API_KEY = environ.get("USER_SERVICE_API_KEY")


class UserServiceAdapter(IUserServicePort):
    def __init__(
        self,
        client: httpx.AsyncClient,
    ):
        self.client = client
        self.base_url = USER_SERVICE_URL
        self.headers = {"Authorization": f"Bearer {USER_SERVICE_API_KEY}"}

    async def get_user_exists(self, user_id: int) -> bool:
        url = f"{self.base_url}/{user_id}"

        try:
            response = await self.client.get(url, headers=self.headers)
            return response.status_code == 200
        except httpx.HTTPError as e:
            raise UserServiceError()
