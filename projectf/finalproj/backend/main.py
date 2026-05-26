from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import datetime

# Import database core assets and models
from backend.database import SessionLocal, Base, engine, Product, Transaction, ChatMessage
from backend import chat 

# Automatically create all tables in marketplace.db if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="RTU Marketplace Backend")

# --- CORS MIDDLEWARE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- INCLUDE WEBSOCKET ROUTER ---
app.include_router(chat.router)


# --- PYDANTIC SCHEMAS FOR VALIDATION ---
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class BuyRequest(BaseModel):
    product_id: int
    buyer_username: str

class ProductCreateRequest(BaseModel):
    product_type: str
    description: str
    price: float
    owner_username: str
    images: Optional[str] = ""
    uniform_type: Optional[str] = ""
    book_title: Optional[str] = ""
    product_name: Optional[str] = ""
    size: Optional[str] = ""


# --- DATABASE SESSION HELPER ---
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- AUTHENTICATION ENDPOINTS ---

@app.post("/register")
def register_user(req: RegisterRequest):
    return {
        "status": "success",
        "message": "User registered successfully",
        "user": {"username": req.username, "email": req.email}
    }

@app.post("/login")
def login_user(req: LoginRequest):
    if not req.username or not req.password:
        raise HTTPException(status_code=400, detail="Missing username or password")
    
    return {
        "status": "success",
        "message": "Welcome back!",
        "user": {"username": req.username, "email": f"{req.username}@rtu.edu.ph"}
    }


# --- PRODUCT MANAGEMENT ---

@app.get("/products")
def get_available_products(db: Session = Depends(get_db_session)):
    products = db.query(Product).filter(Product.is_sold == False).all()
    return [
        {
            "id": p.id,
            "product_type": p.product_type,
            "description": p.description,
            "price": p.price,
            "owner_username": p.owner_username,
            "images": p.images,
        }
        for p in products
    ]

@app.post("/add-product")
def add_product(req: ProductCreateRequest, db: Session = Depends(get_db_session)):
    new_product = Product(
        product_type=req.product_type,
        description=req.description,
        price=req.price,
        owner_username=req.owner_username,
        images=req.images,
        is_sold=False
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return {"status": "success", "product_id": new_product.id}


# --- TRANSACTION MANAGEMENT ---

@app.post("/buy-product")
def buy_product(req: BuyRequest, db: Session = Depends(get_db_session)):
    product = db.query(Product).filter(Product.id == req.product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.is_sold:
        raise HTTPException(status_code=400, detail="This item has already been sold!")
    if product.owner_username == req.buyer_username:
        raise HTTPException(status_code=400, detail="You cannot purchase your own product listing.")

    product.is_sold = True

    transaction_record = Transaction(
        product_id=product.id,
        product_name=product.product_type,
        seller_username=product.owner_username,
        buyer_username=req.buyer_username,
        price=product.price
    )
    
    db.add(transaction_record)
    db.commit()
    
    return {"status": "success", "message": "Item purchased successfully!"}


@app.get("/my-products/{username}")
def get_my_products(username: str, db: Session = Depends(get_db_session)):
    products = db.query(Product).filter(Product.owner_username == username).all()
    return [
        {
            "product_type": p.product_type,
            "price": p.price,
            "images": p.images,
            "is_sold": p.is_sold
        } for p in products
    ]


@app.get("/my-transactions/{username}")
def get_my_transactions(username: str, db: Session = Depends(get_db_session)):
    txs = db.query(Transaction).filter(
        (Transaction.buyer_username == username) | 
        (Transaction.seller_username == username)
    ).all()
    return [
        {
            "product_name": t.product_name,
            "seller_username": t.seller_username,
            "buyer_username": t.buyer_username,
            "price": t.price
        } for t in txs
    ]