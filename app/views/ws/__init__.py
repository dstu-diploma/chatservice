from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketException,
)

from app.controllers.ws import IWebsocketController, get_websocket_controller
from app.controllers.auth import get_user_dto_from_token


router = APIRouter(prefix="")


@router.websocket("/ws")
async def websocket_endpoint(
    socket: WebSocket,
    ws_controller: IWebsocketController = Depends(get_websocket_controller),
):
    try:
        await socket.accept()
        token = await socket.receive_text()
        user_dto = get_user_dto_from_token(token)

        if not ws_controller.is_connected(user_dto.user_id):
            await ws_controller.register_connect(user_dto.user_id, socket)

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
            await ws_controller.register_disconnect(socket.scope["user_id"])
