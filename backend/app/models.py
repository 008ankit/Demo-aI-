
from sqlalchemy import Column, Integer, String, Float, DateTime, func, UniqueConstraint
from .database import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, index=True)
    query = Column(String, index=True)
    title = Column(String)
    price = Column(String)
    rating = Column(String)
    image = Column(String)
    fetched_at = Column(DateTime, default=func.now())

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    __table_args__ = (
        UniqueConstraint('username', name='uq_user_username'),
        UniqueConstraint('email', name='uq_user_email'),
    )
