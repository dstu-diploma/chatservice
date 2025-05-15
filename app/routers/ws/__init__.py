from app.services.ws.interfaces import IWebsocketManager
from app.services.auth import get_user_dto_from_token
from app.dependencies import get_websocket_manager

from fastapi import (
    WebSocketException,
    HTTPException,
    WebSocket,
    APIRouter,
    Depends,
)


router = APIRouter(prefix="")


@router.websocket("/ws")
async def websocket_endpoint(
    socket: WebSocket,
    ws_manager: IWebsocketManager = Depends(get_websocket_manager),
):
    try:
        await socket.accept()
        token = await socket.receive_text()
        user_dto = get_user_dto_from_token(token)

        if not ws_manager.is_connected(user_dto.user_id):
            await ws_manager.register_connect(user_dto, socket)

        while True:
            await socket.receive()

    except WebSocketException as e:
        await socket.close(e.code)
    except HTTPException as e:
        await socket.close()
    except Exception as e:
        pass
    finally:
        if "user_id" in socket.scope:
            await ws_manager.register_disconnect(socket.scope["user_id"])
