from collections import defaultdict
from app.ports.hackathonservice.exceptions import HackathonServiceError
from app.ports.hackathonservice.dto import HackathonDto
from typing import Protocol


class IHackathonServicePort(Protocol):
    base_url: str

    async def get_hackathon_data(self, hackathon_id: int) -> HackathonDto: ...
    async def get_hackathon_data_many(
        self, hackathon_ids: frozenset[int]
    ) -> list[HackathonDto]: ...
    async def can_edit_team_registry(self, hackathon_id: int) -> bool: ...
    async def can_upload_submissions(self, hackathon_id: int) -> bool: ...

    def get_name_map(
        self, hackathons: list[HackathonDto]
    ) -> defaultdict[int, str | None]:
        name_map: defaultdict[int, str | None] = defaultdict(lambda: None)

        for hackathon in hackathons:
            name_map[hackathon.id] = hackathon.name

        return name_map

    async def try_get_hackathon_data(
        self, hackathon_id: int
    ) -> HackathonDto | None:
        try:
            return await self.get_hackathon_data(hackathon_id)
        except Exception as e:
            return None

    async def get_hackathon_exists(self, hackathon_id: int) -> bool:
        return await self.try_get_hackathon_data(hackathon_id) is not None

    async def try_get_hackathon_data_many(
        self, hackathon_ids: frozenset[int]
    ) -> list[HackathonDto]:
        try:
            return await self.get_hackathon_data_many(hackathon_ids)
        except HackathonServiceError:
            return []
