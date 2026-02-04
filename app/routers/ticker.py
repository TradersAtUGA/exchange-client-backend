from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas.ticker import TickerOut
from app.models.ticker import Ticker

from app.core.db import get_session
router = APIRouter(prefix="/ticker", tags=["ticker"])

@router.get("/", response_model=List[TickerOut], status_code=status.HTTP_200_OK)
async def get_tickers(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Ticker))
    tickers = result.scalars().all()
    return tickers

@router.get("/{ticker_id}", response_model=TickerOut, status_code=status.HTTP_200_OK)
async def get_ticker(ticker_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Ticker).where(Ticker.ticker_id == ticker_id))
    ticker = result.scalar_one_or_none()
    if not ticker:
        raise HTTPException(status_code=404, detail="Ticker not found")
    return ticker

@router.get("/symbol/{symbol}", response_model=TickerOut, status_code=status.HTTP_200_OK)
async def get_ticker_by_symbol(symbol: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Ticker).where(Ticker.symbol == symbol))
    ticker = result.scalar_one_or_none()
    if not ticker:
        raise HTTPException(status_code=404, detail="Ticker not found")
    return ticker