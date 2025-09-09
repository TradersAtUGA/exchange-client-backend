from fastapi import APIRouter, Depends, HTTPException 
from sqlalchemy import text                           
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_session
from app.core.dependencies import get_current_user
from app.models.user import User


router = APIRouter(prefix="/healthcheck", tags=["health"])

@router.get("/")
async def healthcheck():
    """Check container is running"""
    return {"status": "ok"}

@router.get("/db")
async def db_health(db: AsyncSession = Depends(get_session)):
    """Check db connection works"""
    try:
        r = await db.execute(text("SELECT 1"))
        return {"db": "ok", "result": r.scalar_one()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")
    
@router.get("/auth")
async def auth_check(curr_user: User = Depends(get_current_user)):
    """Check JWT flow works"""
    return {"status": "ok", "userId": curr_user.userId, "email": curr_user.email}