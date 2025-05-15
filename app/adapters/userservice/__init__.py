from os import environ
from typing import Any, Sequence
import urllib.parse
from fastapi import HTTPException
import httpx

from app.config import Settings
from app.ports.userservice import IUserServicePort
from app.ports.userservice.dto import MinimalUserDto
from app.ports.userservice.exceptions import UserServiceError


class UserServiceAdapter(IUserServicePort):
    def __init__(
        self,
        client: httpx.AsyncClient,
    ):
        self.client = client
        self.base_url = Settings.USER_SERVICE_URL
        self.headers = {
            "Authorization": f"Bearer {Settings.USER_SERVICE_API_KEY}"
        }

    async def _do_get(self, url: str) -> dict:
        try:
            response = await self.client.get(url, headers=self.headers)
            data = response.json()
            if response.status_code == 200:
                return data
            else:
                raise HTTPException(
                    status_code=response.status_code, detail=data["detail"]
                )
        except httpx.HTTPError as e:
            raise UserServiceError()

    async def _do_post(
        self, url: str, body: httpx._types.RequestData | None = None
    ) -> dict:
        try:
            response = await self.client.post(
                url, headers=self.headers, data=body
            )
            data = response.json()
            if response.status_code == 200:
                return data
            else:
                raise HTTPException(
                    status_code=response.status_code, detail=data["detail"]
                )
        except httpx.HTTPError as e:
            raise UserServiceError()

    async def get_user_info(self, user_id: int) -> MinimalUserDto:
        data = await self._do_get(
            urllib.parse.urljoin(self.base_url, str(user_id))
        )
        return MinimalUserDto(**data)

    async def try_get_user_info(self, user_id: int) -> MinimalUserDto | None:
        try:
            return await self.get_user_info(user_id)
        except HTTPException as e:
            return None
