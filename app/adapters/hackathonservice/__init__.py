from typing import Any
from app.ports.hackathonservice.exceptions import HackathonServiceError
from app.ports.hackathonservice import IHackathonServicePort
from app.ports.hackathonservice.dto import HackathonDto
from fastapi import HTTPException
from app.config import Settings
import urllib.parse
import httpx


class HackathonServiceAdapter(IHackathonServicePort):
    def __init__(
        self,
        client: httpx.AsyncClient,
    ):
        self.client = client
        self.base_url = Settings.HACKATHON_SERVICE_URL
        self.headers = {
            "Authorization": f"Bearer {Settings.HACKATHON_SERVICE_API_KEY}"
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
            raise HackathonServiceError()

    async def _do_post(self, url: str, json: Any) -> Any:
        try:
            response = await self.client.post(
                url,
                headers=self.headers,
                json=json,
            )
            data = response.json()
            if response.status_code == 200:
                return data
            else:
                raise HTTPException(
                    status_code=response.status_code, detail=data["detail"]
                )
        except httpx.HTTPError as e:
            raise HackathonServiceError()

    async def get_hackathon_data(self, hackathon_id: int) -> HackathonDto:
        data = await self._do_get(
            urllib.parse.urljoin(self.base_url, str(hackathon_id))
        )
        return HackathonDto(**data)

    async def can_edit_team_registry(self, hackathon_id: int) -> bool:
        data = await self._do_get(
            urllib.parse.urljoin(
                self.base_url, f"{hackathon_id}/can-edit-team-registry"
            )
        )
        return data["can_edit"]

    async def can_upload_submissions(self, hackathon_id: int) -> bool:
        data = await self._do_get(
            urllib.parse.urljoin(
                self.base_url, f"{hackathon_id}/can-upload-submissions"
            )
        )
        return data["can_upload"]

    async def get_hackathon_data_many(
        self, hackathon_ids: frozenset[int]
    ) -> list[HackathonDto]:
        data: list[dict[str, Any]] = await self._do_post(
            urllib.parse.urljoin(self.base_url, "info-many"),
            tuple(hackathon_ids),
        )
        return [HackathonDto(**hackathon) for hackathon in data]
