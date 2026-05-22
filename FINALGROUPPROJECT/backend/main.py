from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from backend.database import engine, Base, get_db
from backend import models, chat

from backend.schemas import UserRegister, UserLogin, ProductCreate
from backend.services.auth_services import register_user, login_user
from backend.models import Product

app = FastAPI()

# CHAT ROUTER
app.include_router(chat.router)

# CREATE TABLES
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

# REGISTER
@app.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    return register_user(db, user.username, user.email, user.password)

# LOGIN
@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    return login_user(db, user.username, user.password)










# ADD PRODUCT
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

    return {
        "status": "success",
        "message": "Product added"
    }

# GET ALL PRODUCTS
@app.get("/products")
def get_products(db: Session = Depends(get_db)):

    products = db.query(Product).all()

    return products

# GET MY PRODUCTS
@app.get("/my-products/{username}")
def get_my_products(username: str, db: Session = Depends(get_db)):

    products = db.query(Product).filter(
        Product.owner_username == username
    ).all()

    return products