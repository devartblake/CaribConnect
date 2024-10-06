from datetime import datetime, timedelta, timezone
from typing import Any
 
import jwt
from jwt import PyJWTError
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY: str = settings.SECRET_KEY
ALGORITHM = "HS256"

def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    # Add user authentication logic
    if username == "user" and password == "password":
        return {"username": username}
    return None

def decode_token(token: str):
    try:
        payload = jwt.decode(token< SECRET_KEY, algorithms=ALGORITHM)
        return payload.get("sub")
    except PyJWTError:
        return None
