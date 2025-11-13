from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.db import get_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.portfolio import Portfolio
from app.schemas.portfolio import PortfolioCreate, PortfolioOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/portfolios", response_model=List[PortfolioOut], status_code=status.HTTP_200_OK)
async def get_user_portfolios(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    @brief Retrieve all portfolios for a given user.
m
    @param user The current user
    @param db Session Database session dependency.
    @return List[PortfolioOut] List of portfolios owned by the user.
    @throws HTTPException 401 if the user is not found.
    """
    result = await db.scalars(select(Portfolio).where(Portfolio.userId == current_user.userId))
    portfolios = result.all()
    return portfolios

@router.post("/portfolios", response_model=PortfolioOut, status_code=status.HTTP_201_CREATED)
async def create_user_portfolio(
    portfolio_data: PortfolioCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    @brief Create a new portfolio for a user.

    @param current_user The current user
    @param portfolio_data PortfolioCreate Payload containing name and description.
    @param db Session Database session dependency.
    @return PortfolioOut The created portfolio record.
    @throws HTTPException 401 if the user is not found.
    """
    new_portfolio = Portfolio(
        userId=current_user.userId,
        name=portfolio_data.name,
        description=portfolio_data.description,
    )

    db.add(new_portfolio)
    await db.commit()
    await db.refresh(new_portfolio)
    return new_portfolio
