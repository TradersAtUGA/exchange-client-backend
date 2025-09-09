import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from app.core.config import settings

# Password hashing

def hash_password(plain_password: str) -> str:
    """Hash a plain text password using bcrypt."""
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against a bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


#JWT helpers

def create_token(subject: str | int) -> str:
    """Create a JWT Token for the userId passed as input"""
    expires = datetime.now() + timedelta(minutes=settings.JWT_EXPIRE_MIN)
    payload = {"sub":str(subject), "exp":expires}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> dict | None:
    """Decode JWT token passed as input"""
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None