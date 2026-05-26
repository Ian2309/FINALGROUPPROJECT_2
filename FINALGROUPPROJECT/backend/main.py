# backend/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

# Import components exactly as you named them
from backend.database import SessionLocal, engine
from backend.models import Base, Product, Transaction, User
from backend.schemas import UserRegister, UserLogin, ProductCreate, BuyProduct

# Import sub-routers and your auth service layer
from backend import chat_routes, cancel_routes
from backend.auth import register_user, login_user

from backend.chat_ws import router as ws_router


Base.metadata.create_all(bind=engine)

app = FastAPI(title="RTU Marketplace Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach modular sub-routers

app.include_router(chat_routes.router, prefix="/chat", tags=["Chat"])
app.include_router(cancel_routes.router, prefix="/action", tags=["Management"])
app.include_router(ws_router)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- AUTHENTICATION ENDPOINTS ---

@app.post("/register")
def register(req: UserRegister):
    result = register_user(username=req.username, email=req.email, password=req.password)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.post("/login")
def login(req: UserLogin):
    result = login_user(username=req.username, password=req.password)
    if result["status"] == "error":
        raise HTTPException(status_code=401, detail=result["message"])
    return result

@app.get("/user/{username}")
def get_user(username: str, db: Session = Depends(get_db)):

    user = db.query(User).filter(
        User.username == username
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "username": user.username,
        "email": user.email
    }

# --- NEW: LOGOUT VALIDATION ENDPOINT ---
@app.post("/logout")
def logout(username: str):
    """
    Validates and logs out the user session. 
    Without JWT, this explicitly signals the backend that the client session has terminated.
    """
    return {
        "status": "success",
        "message": f"User {username} successfully logged out. Session invalidated."
    }


# --- BUSINESS LOGIC ENDPOINTS ---

@app.get("/products")
def get_available_products(db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.is_sold == "No").all()
    return [
        {
            "id": p.id,
            "product_type": p.product_type,
            "uniform_type": p.uniform_type,
            "book_title": p.book_title,
            "product_name": p.product_name,
            "size": p.size,
            "price": p.price,
            "description": p.description,
            "owner_username": p.owner_username,
            "images": p.images,
            "is_sold": p.is_sold,
            "created_at": p.created_at
        }
        for p in products
    ]

@app.post("/add-product")
def add_product(req: ProductCreate, db: Session = Depends(get_db)):
    new_product = Product(
        product_type=req.product_type,
        uniform_type=req.uniform_type,
        book_title=req.book_title,
        product_name=req.product_name,
        size=req.size,
        price=str(req.price), 
        description=req.description,
        owner_username=req.owner_username,
        images=req.images,
        is_sold="No"
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return {"status": "success", "product_id": new_product.id}

@app.post("/buy-product")
def buy_product(req: BuyProduct, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == req.product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.is_sold == "Yes":
        raise HTTPException(status_code=400, detail="This item has already been sold!")

    product.is_sold = "Yes"
    resolved_name = product.product_name or product.book_title or product.uniform_type or "Marketplace Item"

    transaction_record = Transaction(
        product_id=product.id,
        product_name=resolved_name,
        seller_username=product.owner_username,
        buyer_username=req.buyer_username,
        price=int(product.price) if product.price.isdigit() else 0,
        status="Completed"
    )
    db.add(transaction_record)
    db.commit()
    return {"status": "success", "message": "Item purchased successfully!"}

@app.get("/my-products/{username}")
def get_my_products(username: str, db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.owner_username == username).all()
    return [
        {
            "id": p.id,
            "product_type": p.product_type,
            "product_name": p.product_name or p.book_title or p.uniform_type,
            "price": p.price,
            "images": p.images,
            "is_sold": p.is_sold
        } for p in products
    ]

@app.get("/my-transactions/{username}")
def get_my_transactions(username: str, db: Session = Depends(get_db)):
    txs = db.query(Transaction).filter(
        (Transaction.buyer_username == username) | 
        (Transaction.seller_username == username)
    ).all()

    return [
    {
        "id": t.id,
        "product_id": t.product_id,
        "product_name": t.product_name,
        "seller_username": t.seller_username,
        "buyer_username": t.buyer_username,
        "price": t.price,
        "status": t.status,
        "created_at": t.created_at
    } for t in txs
]