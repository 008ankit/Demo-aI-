
from sqlalchemy.orm import Session
from .models import Product
from datetime import datetime, timedelta

CACHE_TTL = timedelta(hours=6)

def get_cached(db: Session, platform: str, query: str):
    cutoff = datetime.utcnow() - CACHE_TTL
    return db.query(Product).filter(Product.platform==platform, Product.query==query, Product.fetched_at>=cutoff).all()

def cache_products(db: Session, platform: str, query: str, items: list[dict]):
    db.query(Product).filter(Product.platform==platform, Product.query==query).delete()
    for item in items:
        db.add(Product(platform=platform, query=query, **item))
    db.commit()

def format_products(db_items):
    return [{"title": p.title, "price": p.price, "rating": p.rating, "image": p.image} for p in db_items]
