from app.adapters.event_consumer.aiopika import AioPikaEventConsumerAdapter
from app.adapters.hackathonservice import HackathonServiceAdapter
from app.ports.hackathonservice import IHackathonServicePort
from app.services.requests.interfaces import IRequestService
from app.services.requests.service import RequestService
from app.services.ws.interfaces import IWebsocketManager
from app.ports.event_consumer import IEventConsumerPort
from app.adapters.userservice import UserServiceAdapter
from app.services.ws.service import WebsocketManager
from app.ports.userservice import IUserServicePort
from app.config import Settings
from functools import lru_cache
from fastapi import Depends
import httpx


async def get_http_client():
    return httpx.AsyncClient()


@lru_cache
def get_event_consumer() -> IEventConsumerPort:
    return AioPikaEventConsumerAdapter(
        Settings.RABBITMQ_URL, "events", queue_name="chatservice"
    )


@lru_cache
def get_user_service(
    client: httpx.AsyncClient = Depends(get_http_client),
) -> IUserServicePort:
    return UserServiceAdapter(client)


@lru_cache
def get_hackathon_service(
    client: httpx.AsyncClient = Depends(get_http_client),
) -> IHackathonServicePort:
    return HackathonServiceAdapter(client)


@lru_cache
def get_request_service(
    user_service: IUserServicePort = Depends(get_user_service),
    hackathon_service: IHackathonServicePort = Depends(get_hackathon_service),
) -> IRequestService:
    return RequestService(user_service, hackathon_service)


@lru_cache
def get_websocket_manager() -> IWebsocketManager:
    return WebsocketManager()
