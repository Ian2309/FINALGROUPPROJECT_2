from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
from typing import Dict
from backend.database import SessionLocal, ChatMessage

router = APIRouter(prefix="/ws/chat")

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, username: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[username] = websocket
        
        # Load historical logs from the database upon establishing connection
        db = SessionLocal()
        try:
            history = db.query(ChatMessage).filter(
                (ChatMessage.receiver == None) | 
                (ChatMessage.sender == username) | 
                (ChatMessage.receiver == username)
            ).order_by(ChatMessage.timestamp.asc()).all()
            
            for msg in history:
                if not msg.receiver:
                    await websocket.send_text(f"💬 {msg.sender}: {msg.message}")
                else:
                    if msg.sender == username:
                        await websocket.send_text(f"🔒 [Private to {msg.receiver}]: {msg.message}")
                    else:
                        await websocket.send_text(f"🔒 [Private] {msg.sender}: {msg.message}")
        finally:
            db.close()

    def disconnect(self, username: str):
        if username in self.active_connections:
            del self.active_connections[username]

    async def send_private_message(self, message: str, sender: str, receiver: str):
        if receiver in self.active_connections:
            websocket = self.active_connections[receiver]
            await websocket.send_text(f"🔒 [Private] {sender}: {message}")
        else:
            if sender in self.active_connections:
                await self.active_connections[sender].send_text(f"⚠️ System: {receiver} is offline. Message saved to inbox.")

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
    db = SessionLocal()
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            
            receiver_id = payload.get("receiver_id")
            message_text = payload.get("message")

            if not message_text:
                continue

            target_receiver = receiver_id if receiver_id else None

            new_msg = ChatMessage(sender=user_id, receiver=target_receiver, message=message_text)
            db.add(new_msg)
            db.commit()

            if target_receiver:
                await manager.send_private_message(message_text, sender=user_id, receiver=target_receiver)
                await websocket.send_text(f"🔒 [Private to {target_receiver}]: {message_text}")
            else:
                await manager.broadcast(f"💬 {user_id}: {message_text}")
                break 

    except WebSocketDisconnect:
        manager.disconnect(user_id)
    finally:
        db.close()