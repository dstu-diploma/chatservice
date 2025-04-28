import json
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketException,
)

from app.controllers.ws import WebsocketController, get_websocket_controller
from app.views.ws.auth import get_message_header


router = APIRouter(prefix="")


@router.websocket("/ws")
async def websocket_endpoint(
    socket: WebSocket,
    ws_controller: WebsocketController = Depends(get_websocket_controller),
):
    try:
        await socket.accept()

        while True:
            data = await socket.receive_text()
            message_data: dict = json.loads(data)
            header = get_message_header(message_data)

            if not ws_controller.is_connected(header.user_id):
                ws_controller.register_connect(header.user_id, socket)

            await ws_controller.run_action(
                header.user_id, header.action, message_data.get("data", {})
            )

    except WebSocketException as e:
        await socket.close(e.code)
    except HTTPException as e:
        await socket.close()
