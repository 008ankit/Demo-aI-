
from sqlalchemy import Column, Integer, String, Float, DateTime, func, UniqueConstraint
from .database import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String, index=True)
    product_name = Column(String)
    category = Column(String)
    category_1 = Column(String)
    category_2 = Column(String)
    category_3 = Column(String)
    discounted_price = Column(String)
    actual_price = Column(String)
    discount_percentage = Column(String)
    rating = Column(String)
    product_rating = Column(String)
    rating_count = Column(String)
    seller_name = Column(String)
    seller_rating = Column(String)
    about_product = Column(String)
    description = Column(String)
    highlights = Column(String)
    user_id = Column(String)
    user_name = Column(String)
    review_id = Column(String)
    review_title = Column(String)
    review_content = Column(String)
    img_link = Column(String)
    image_links = Column(String)
    product_link = Column(String)
    platform = Column(String, index=True)
    query = Column(String, index=True)
    fetched_at = Column(DateTime, default=func.now())
    # Flipkart and ElectronicsData fields
    Brand = Column(String)
    Model = Column(String)
    Color = Column(String)
    Memory = Column(String)
    Storage = Column(String)
    Selling_Price = Column(String)
    Original_Price = Column(String)
    Sub_Category = Column(String)
    Price = Column(String)
    Discount = Column(String)
    Currency = Column(String)
    Feature = Column(String)
    # Data - Copy.csv fields
    data_copy_id = Column(String)
    data_copy_brand = Column(String)
    sold_price = Column(String)
    url = Column(String)
    img = Column(String)

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
