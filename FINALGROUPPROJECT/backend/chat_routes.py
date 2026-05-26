#chat_routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from backend.database import get_db
from backend.models import Conversation, Message
from backend.chat_service import save_message

router = APIRouter()


# =========================
# OPEN / CREATE CONVERSATION
# =========================
@router.post("/chat/open")
def open_chat(payload: dict, db: Session = Depends(get_db)):

    convo = db.query(Conversation).filter(
        and_(
            Conversation.buyer_username == payload["buyer"],
            Conversation.seller_username == payload["seller"],
            Conversation.product_id == payload["product_id"]
        )
    ).first()

    if not convo:
        convo = Conversation(
            buyer_username=payload["buyer"],
            seller_username=payload["seller"],
            product_id=payload["product_id"]
        )
        db.add(convo)
        db.commit()
        db.refresh(convo)

    return {
        "conversation_id": convo.id
    }


# =========================
# GET CONVERSATIONS
# =========================
@router.get("/conversations/{username}")
def get_conversations(username: str, db: Session = Depends(get_db)):

    convos = db.query(Conversation).filter(
        or_(
            Conversation.buyer_username == username,
            Conversation.seller_username == username
        )
    ).all()

    result = []

    for c in convos:

        other_user = (
            c.seller_username if c.buyer_username == username
            else c.buyer_username
        )

        last_msg = db.query(Message).filter(
            Message.conversation_id == c.id
        ).order_by(Message.created_at.desc()).first()

        result.append({
            "conversation_id": c.id,
            "other_user": other_user,
            "product_id": c.product_id,
            "last_message": last_msg.content if last_msg else ""
        })

    return result


# =========================
# GET MESSAGES
# =========================
@router.get("/messages/{conversation_id}")
def get_messages(conversation_id: int, db: Session = Depends(get_db)):

    msgs = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).all()

    return [
        {
            "sender": m.sender_username,
            "message": m.content,
            "timestamp": m.created_at
        }
        for m in msgs
    ]


# =========================
# SEND MESSAGE
# =========================
@router.post("/send-message")
def send_message(payload: dict, db: Session = Depends(get_db)):

    msg = save_message(
        db,
        payload["conversation_id"],
        payload["sender"],
        payload["message"]
    )

    return {
        "status": "success",
        "message_id": msg.id
    }

@router.get("/conversation/{conversation_id}")
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):

    convo = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    return {
        "buyer": convo.buyer_username,
        "seller": convo.seller_username,
        "product_id": convo.product_id
    }