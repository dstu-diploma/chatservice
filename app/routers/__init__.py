from .root import router as root_router
from .ws import router as ws_router
from fastapi import APIRouter

main_router = APIRouter()

main_router.include_router(ws_router)
main_router.include_router(root_router)
