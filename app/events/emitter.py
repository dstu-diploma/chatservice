from pyee.asyncio import AsyncIOEventEmitter
from enum import StrEnum


class Events(StrEnum):
    Message = "message"
    RequestOpened = "request_opened"
    RequestClosed = "request_closed"


class ExternalEvents(StrEnum):
    UserBanned = "user.banned"
    UserDeleted = "user.deleted"
    TeamHackathonTeamDeleted = "team.hackathon_team_deleted"
    HackathonDeleted = "hackathon.deleted"


Emitter = AsyncIOEventEmitter()
