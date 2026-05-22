from sqlalchemy import Column, Integer, String
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