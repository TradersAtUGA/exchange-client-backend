from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.db import get_session
from app.core.security import decode_token
from app.models.user import User

# Used to extract token string from authorization header
bearer_scheme = HTTPBearer(auto_error=True) 

async def get_current_user(
        creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        session: AsyncSession = Depends(get_session),
        ) -> User:
    """Resolve and return the authenticated User for the incoming request."""

    #Decode token and check if it is still valid/exists
    token = creds.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    
    #get userId from payload
    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Malformed token")

    #Lookup user by userId
    user = await session.scalar(select(User).where(User.userId == int(sub)))
    if not user:
        # Token could be valid cryptographically but refer to a deleted/disabled user
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user