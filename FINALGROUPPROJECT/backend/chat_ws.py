#backend/chat_ws.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

connections = {}

@router.websocket("/chat/ws/{conversation_id}")
async def chat_ws(websocket: WebSocket, conversation_id: int):

    await websocket.accept()

    if conversation_id not in connections:
        connections[conversation_id] = []

    connections[conversation_id].append(websocket)

    try:
        while True:
            data = await websocket.receive_json()

            # safe broadcast
            for conn in list(connections[conversation_id]):
                try:
                    await conn.send_json({
                        "sender": data.get("sender"),
                        "message": data.get("message")
                    })
                except:
                    connections[conversation_id].remove(conn)

    except WebSocketDisconnect:
        if websocket in connections.get(conversation_id, []):
            connections[conversation_id].remove(websocket)