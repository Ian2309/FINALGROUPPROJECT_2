# chat_service.py
from sqlalchemy.orm import Session
from backend.models import Message


def save_message(db: Session, conversation_id: int, sender_username: str, content: str):

    msg = Message(
        conversation_id=conversation_id,
        sender_username=sender_username,
        content=content
    )

    db.add(msg)
    db.commit()
    db.refresh(msg)

    return msg