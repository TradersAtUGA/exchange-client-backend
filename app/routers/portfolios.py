from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.db import get_session
from app.models.portfolio import Portfolio
from app.models.holding import Holding
from app.models.transaction import Transaction
from app.schemas.holding import HoldingOut
from app.schemas.transaction import TransactionOut

router = APIRouter(prefix="/portfolios", tags=["portfolios"])

@router.get("/{portfolioid}/holdings", response_model=List[HoldingOut], status_code=status.HTTP_200_OK)
async def get_portfolio_holdings(portfolioid: int, session: AsyncSession = Depends(get_session)):
    """
    @brief Retrieve all holdings for a given portfolio.

    @param portfolioid int The portfolio identifier.
    @param session AsyncSession Database session dependency.
    @return List[HoldingOut] List of holdings associated with the portfolio.
    @throws HTTPException 404 if the portfolio is not found.
    """
    result = await session.execute(select(Portfolio).where(Portfolio.portfolioId == portfolioid))
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # get all holdings
    result = await session.execute(
        select(Holding).where(Holding.portfolioId == portfolioid).order_by(Holding.holdingId)
    )
    holdings = result.scalars().all()
    return holdings

@router.get("/{portfolioid}/transactions", response_model=List[TransactionOut], status_code=status.HTTP_200_OK)
async def get_portfolio_transactions(portfolioid: int, session: AsyncSession = Depends(get_session)):
    """
    @brief Retrieve all transactions tied to a given portfolio.

    @param portfolioid int The portfolio identifier.
    @param session AsyncSession Database session dependency.
    @return List[TransactionOut] List of transactions associated with the portfolio.
    @throws HTTPException 404 if the portfolio is not found.
    """
    result = await session.execute(select(Portfolio).where(Portfolio.portfolioId == portfolioid))
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # get all transactions
    result = await session.execute(
        select(Transaction).where(Transaction.portfolioId == portfolioid).order_by(Transaction.transactionId)
    )
    transactions = result.scalars().all()
    return transactions