#main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.database import engine, Base, get_db
from backend import chat

from backend.schemas import UserRegister, UserLogin, ProductCreate, BuyProduct
from backend.services.auth_services import register_user, login_user
from backend.models import Product, Transaction

app = FastAPI()

# CHAT ROUTER
app.include_router(chat.router)


# ---------------- CREATE TABLES ----------------
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


# ---------------- REGISTER ----------------
@app.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    return register_user(db, user.username, user.email, user.password)


# ---------------- LOGIN ----------------
@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    return login_user(db, user.username, user.password)


# ---------------- ADD PRODUCT ----------------
@app.post("/add-product")
def add_product(product: ProductCreate, db: Session = Depends(get_db)):

    new_product = Product(
        product_type=product.product_type,
        uniform_type=product.uniform_type,
        book_title=product.book_title,
        product_name=product.product_name,
        size=product.size,
        price=product.price,
        description=product.description,
        owner_username=product.owner_username,
        images=product.images
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {"status": "success", "message": "Product added"}


# ---------------- GET ALL PRODUCTS ----------------
@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()


# ---------------- MY PRODUCTS ----------------
@app.get("/my-products/{username}")
def get_my_products(username: str, db: Session = Depends(get_db)):

    return db.query(Product).filter(
        Product.owner_username == username
    ).all()


# ---------------- BUY PRODUCT ----------------
@app.post("/buy-product")
def buy_product(data: BuyProduct, db: Session = Depends(get_db)):

    product = db.query(Product).filter(Product.id == data.product_id).first()

    if not product:
        return {
            "status": "error",
            "message": "Product not found"
        }

    # prevent self purchase
    if product.owner_username.lower() == data.buyer_username.lower():
        return {
            "status": "error",
            "message": "You cannot buy your own product"
        }

    # prevent sold items
    if product.is_sold == "Yes":
        return {
            "status": "error",
            "message": "Product already sold"
        }

    transaction = Transaction(
        product_id=product.id,
        product_name=product.product_name or product.book_title or product.product_type,
        buyer_username=data.buyer_username,
        seller_username=product.owner_username,
        price=int(product.price)
    )

    db.add(transaction)

    # MARK PRODUCT SOLD
    product.is_sold = "Yes"

    db.commit()

    return {
        "status": "success",
        "message": "Product purchased"
    }


# ---------------- MY TRANSACTIONS ----------------
@app.get("/my-transactions/{username}")
def my_transactions(username: str, db: Session = Depends(get_db)):

    return db.query(Transaction).filter(
        or_(
            Transaction.buyer_username == username,
            Transaction.seller_username == username
        )
    ).all()