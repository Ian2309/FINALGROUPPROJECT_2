from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
from typing import Dict

router = APIRouter(prefix="/ws/chat")

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, username: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[username] = websocket

    def disconnect(self, username: str):
        if username in self.active_connections:
            del self.active_connections[username]

    async def send_private_message(self, message: str, sender: str, receiver: str):
        if receiver in self.active_connections:
            websocket = self.active_connections[receiver]
            await websocket.send_text(f"🔒 [Private] {sender}: {message}")
        else:
            if sender in self.active_connections:
                await self.active_connections[sender].send_text(f"⚠️ System: {receiver} is offline.")

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

@router.websocket("/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            
            receiver_id = payload.get("receiver_id")
            message_text = payload.get("message")

            if not message_text:
                continue

            if receiver_id:
                await manager.send_private_message(message_text, sender=user_id, receiver=receiver_id)
                await websocket.send_text(f"🔒 [Private to {receiver_id}]: {message_text}")
            else:
                await manager.broadcast(f"💬 {user_id}: {message_text}")
                break 

    except WebSocketDisconnect:
        manager.disconnect(user_id)