from pydantic import BaseModel
from typing import Optional


# ---------------- USER ----------------
class UserRegister(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


# ---------------- PRODUCT ----------------
class ProductCreate(BaseModel):
    product_type: str

    uniform_type: Optional[str] = None
    book_title: Optional[str] = None
    product_name: Optional[str] = None

    size: Optional[str] = None
    price: int
    description: str

    owner_username: str

    images: Optional[str] = ""


# ---------------- BUY PRODUCT ----------------
class BuyProduct(BaseModel):
    product_id: int
    buyer_username: str