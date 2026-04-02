from datetime import datetime, timedelta
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode: dict[str, Any] = {"sub": subject, "exp": expire, "type": "access"}
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def create_refresh_token(subject: str) -> str:
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode: dict[str, Any] = {"sub": subject, "exp": expire, "type": "refresh"}
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
