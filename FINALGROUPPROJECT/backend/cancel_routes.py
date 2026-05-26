from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Transaction

router = APIRouter()

@router.post("/cancel-order/{transaction_id}")
def cancel_order(transaction_id: int, db: Session = Depends(get_db)):

    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id
    ).first()

    if not transaction:
        return {"status": "error", "message": "Transaction not found"}

    transaction.status = "Cancelled"

    db.commit()

    return {"status": "success", "message": "Order cancelled"}