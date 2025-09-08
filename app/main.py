from fastapi import FastAPI, Depends, HTTPException 
from sqlalchemy import text                           
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_session

app = FastAPI(title="Exchange Client Backend")

@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}

@app.get("/healthcheck/db")
async def db_health(db: AsyncSession = Depends(get_session)):
    try:
        r = await db.execute(text("SELECT 1"))
        return {"db": "ok", "result": r.scalar_one()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")