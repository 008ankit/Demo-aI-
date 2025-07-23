from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from .models import Base, User
from .crud import get_cached, cache_products, format_products
from .scraping import get_flipkart, get_amazon
from .chatgpt import ask_chatgpt, ask_chatgpt_general  # Updated to return JSON from GPT
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
import datetime



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:5502",
        "http://127.0.0.1:5502"
    ],
    allow_methods=["*"],
    allow_headers=["*"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict, expires_delta: datetime.timedelta = None):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + (expires_delta or datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) # type: ignore

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) # type: ignore
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

class AuthRequest(BaseModel):
    fullname: str = None
    email: str = None
    username: str
    password: str

@app.post("/login")
def login(auth: AuthRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == auth.username).first()
    if not user or not pwd_context.verify(auth.password, user.password_hash):
        return {"success": False, "message": "Invalid username or password."}
    # Create JWT token
    access_token = create_access_token(data={"sub": user.username})
    return {"success": True, "message": "Login successful!", "token": access_token}

@app.post("/signup")
def signup(auth: AuthRequest, db: Session = Depends(get_db)):
    # Check if user or email exists
    if db.query(User).filter(User.username == auth.username).first():
        return {"success": False, "message": "Username already exists."}
    if db.query(User).filter(User.email == auth.email).first():
        return {"success": False, "message": "Email already exists."}
    # Hash password
    hashed = pwd_context.hash(auth.password)
    user = User(fullname=auth.fullname, email=auth.email, username=auth.username, password_hash=hashed)
    db.add(user)
    db.commit()
    return {"success": True, "message": "Sign up successful!"}

@app.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "fullname": current_user.fullname,
        "email": current_user.email,
        "username": current_user.username
    }

@app.get("/search")
def search(query: str, db: Session = Depends(get_db)):
    results = {}

    for platform, scraper in [("flipkart", get_flipkart), ("amazon", get_amazon)]:
        cached = get_cached(db, platform, query)
        if cached:
            results[platform] = format_products(cached)
        else:
            items = scraper(query)
            if items:
                cache_products(db, platform, query, items)
                results[platform] = items
            else:
                results[platform] = []

    # If no products found, always return intro + product list (no confirmation)
    if not (results["flipkart"] or results["amazon"]):
        ai_response = ask_chatgpt(query)
        return {"source": "ai", "ai_response": ai_response}

    return {"source": "scraper", "results": results}

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat_endpoint(chat: ChatRequest):
    return ask_chatgpt_general(chat.message)
