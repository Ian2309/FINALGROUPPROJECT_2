#models.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True)
    password = Column(String)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    product_type = Column(String)
    uniform_type = Column(String)
    book_title = Column(String)
    product_name = Column(String)
    size = Column(String)
    price = Column(String)
    description = Column(String)
    owner_username = Column(String)
    images = Column(String)

    is_sold = Column(String, default="No")

    created_at = Column(DateTime, default=datetime.utcnow)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    product_id = Column(Integer, ForeignKey("products.id"))

    product_name = Column(String)

    buyer_username = Column(String)
    seller_username = Column(String)
    price = Column(Integer)

   
    created_at = Column(DateTime, default=datetime.utcnow)