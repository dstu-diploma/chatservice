from app.services.requests.interfaces import IRequestService
from app.services.requests.service import RequestService
from app.services.ws.interfaces import IWebsocketManager
from app.adapters.userservice import UserServiceAdapter
from app.services.ws.service import WebsocketManager
from app.ports.userservice import IUserServicePort
from functools import lru_cache
from fastapi import Depends
import httpx


async def get_http_client():
    async with httpx.AsyncClient() as client:
        yield client


@lru_cache
def get_user_service(
    client: httpx.AsyncClient = Depends(get_http_client),
) -> IUserServicePort:
    return UserServiceAdapter(client)


@lru_cache
def get_request_service(
    user_service: IUserServicePort = Depends(get_user_service),
) -> IRequestService:
    return RequestService(user_service)


@lru_cache
def get_websocket_manager() -> IWebsocketManager:
    return WebsocketManager()
