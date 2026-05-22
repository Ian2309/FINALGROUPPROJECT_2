from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        # Maps user_id (str) to their active WebSocket connection
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: str, receiver_id: str):
        """Sends a private message to a specific user"""
        if receiver_id in self.active_connections:
            await self.active_connections[receiver_id].send_text(message)

    async def broadcast(self, message: str):
        """Sends a message to absolutely everyone connected"""
        for connection in self.active_connections.values():
            await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/chat/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(user_id, websocket)
    try:
        # Broadcast that a user has joined the chat
        await manager.broadcast(f"User {user_id} has joined the chat.")
        
        while True:
            # Expecting JSON data like: {"receiver_id": "user2", "message": "Hello!"}
            data = await websocket.receive_json()
            receiver_id = data.get("receiver_id")
            message_text = data.get("message")
            
            formatted_message = f"{user_id}: {message_text}"
            
            if receiver_id:
                # Private message endpoint (End-to-End Chat)
                await manager.send_personal_message(formatted_message, receiver_id)
                # Also echo the message back to the sender so it shows on their screen
                await manager.send_personal_message(formatted_message, user_id)
            else:
                # Fallback to broadcast if no receiver is specified
                await manager.broadcast(formatted_message)
                
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        await manager.broadcast(f"User {user_id} has left the chat.")