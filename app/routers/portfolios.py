from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.db import get_session
from app.core.dependencies import get_current_user
from app.models.portfolio import Portfolio
from app.models.user import User
from app.models.holding import Holding
from app.models.transaction import Transaction
from app.schemas.holding import HoldingOut
from app.schemas.transaction import TransactionOut


router = APIRouter(prefix="/portfolios", tags=["portfolios"])


@router.get("/{portfolioid}/holdings", response_model=List[HoldingOut], status_code=status.HTTP_200_OK)
async def get_portfolio_holdings(
    portfolioid: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    @brief Retrieve all holdings for a given portfolio.

    @param portfolioid int The portfolio identifier.
    @param current_user User The current user
    @param session AsyncSession Database session dependency.
    @return List[HoldingOut] List of holdings associated with the portfolio.
    @throws HTTPException 404 if the portfolio is not found.
    """
    result = await session.execute(
        select(Portfolio).where(
            Portfolio.portfolioId == portfolioid,
            Portfolio.userId == current_user.userId  
        )
    )
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found or unauthorized")

    result = await session.execute(
        select(Holding).where(Holding.portfolioId == portfolioid).order_by(Holding.holdingId)
    )
    holdings = result.scalars().all()
    return holdings


@router.get("/{portfolioid}/transactions", response_model=List[TransactionOut], status_code=status.HTTP_200_OK)
async def get_portfolio_transactions(
    portfolioid: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve all transactions for a given portfolio that belongs to the current user.
    """
    result = await session.execute(
        select(Portfolio).where(
            Portfolio.portfolioId == portfolioid,
            Portfolio.userId == current_user.userId
        )
    )
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found or unauthorized")

    result = await session.execute(
        select(Transaction).where(Transaction.portfolioId == portfolioid).order_by(Transaction.transactionId)
    )
    transactions = result.scalars().all()
    return transactions


