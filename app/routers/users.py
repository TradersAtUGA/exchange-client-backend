from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_session
from app.models.user import User
from app.models.portfolio import Portfolio
from app.schemas.portfolio import PortfolioCreate, PortfolioOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{userid}/portfolios", response_model=List[PortfolioOut], status_code=200)
def get_user_portfolios(userid: int, db: Session = Depends(get_session)):
    """
    @brief Retrieve all portfolios for a given user.

    @param userid int The user's identifier.
    @param db Session Database session dependency.
    @return List[PortfolioOut] List of portfolios owned by the user.
    @throws HTTPException 404 if the user is not found.
    """
    user = db.get(User, userid) if hasattr(db, "get") else db.query(User).filter(User.userId == userid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    portfolios = db.query(Portfolio).filter(Portfolio.userId == userid).all()
    return portfolios

@router.post("/{userid}/portfolios", response_model=PortfolioOut, status_code=201)
async def create_user_portfolio(userid: int, portfolio_data: PortfolioCreate, db: Session = Depends(get_session)):
    """
    @brief Create a new portfolio for a user.

    @param userid int The user's identifier for whom the portfolio will be created.
    @param portfolio_data PortfolioCreate Payload containing name and description.
    @param db Session Database session dependency.
    @return PortfolioOut The created portfolio record.
    @throws HTTPException 404 if the user is not found.
    """
    user = db.get(User, userid) if hasattr(db, "get") else db.query(User).filter(User.userId == userid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_portfolio = Portfolio(
        userId=userid,
        name=portfolio_data.name,
        description=portfolio_data.description
    )
    db.add(new_portfolio)
    await db.commit()
    await db.refresh(new_portfolio)

    return new_portfolio