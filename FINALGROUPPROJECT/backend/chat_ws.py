from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import Message

router = APIRouter(prefix="/chat/ws")

connections = {}


@router.websocket("/{conversation_id}")
async def chat_ws(websocket: WebSocket, conversation_id: int):

    await websocket.accept()

    connections.setdefault(conversation_id, []).append(websocket)

    try:
        while True:
            data = await websocket.receive_json()

            sender = data.get("username")   # FIXED
            message = data.get("message")

            if not sender or not message:
                continue

            # SAVE TO DB
            db: Session = SessionLocal()
            try:
                db.add(Message(
                    conversation_id=conversation_id,
                    sender_username=sender,
                    content=message
                ))
                db.commit()
            finally:
                db.close()

            # BROADCAST
            payload = {
                "sender": sender,
                "message": message
            }

            for conn in list(connections.get(conversation_id, [])):
                try:
                    await conn.send_json(payload)
                except Exception:
                    connections[conversation_id].remove(conn)

    except WebSocketDisconnect:
        connections[conversation_id] = [
            c for c in connections.get(conversation_id, [])
            if c != websocket
        ]