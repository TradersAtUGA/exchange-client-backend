from app.core.db import get_session
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.transaction import Transaction, TransactionType
from app.models.portfolio import Portfolio, User
from app.models.holding import Holding
from app.core.dependencies import get_current_user
from app.schemas.transaction import TransactionPayload


router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_transaction(
    payload: TransactionPayload, 
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    ):
    """
    @brief Create a BUY or SELL transaction and update holdings atomically.

    Acquires a row-level lock on the relevant holding to prevent race conditions.
    Updates weighted average price on BUY and validates sufficient quantity on SELL.

    @param payload TransactionPayload Incoming transaction details including user_id, portfolio_id, ticker_id, type, price_per_share, quantity, and timestamp.
    @param session AsyncSession Database session provided by dependency injection.
    @return dict JSON object containing the created transaction_id and status.
    @throws HTTPException 404 if the user or portfolio does not exist.
    @throws HTTPException 400 if attempting to sell without a holding or with insufficient quantity.
    @throws HTTPException 500 if the transaction fails for any other reason.
    """
    try:
        # Validate portfolio exists
        result = await session.execute(
            select(Portfolio).where(
                Portfolio.portfolioId == payload.portfolio_id,
                Portfolio.userId == current_user.userId
            )
        )
        db_portfolio = result.scalar_one_or_none()
        if not db_portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        #todo validate if payload attributes match live market data
        total = payload.quantity * payload.price_per_share

        
        # Get holding with row-level lock (SELECT FOR UPDATE)
        result = await session.execute(
            select(Holding)
            .where(
                Holding.portfolioId == payload.portfolio_id,
                Holding.ticker_id == payload.ticker_id
            )
            .with_for_update()
        )
        db_holding = result.scalar_one_or_none()

        if payload.type == "BUY":
            if db_holding:
                new_quantity = db_holding.quantity + payload.quantity

                # new avg price
                new_avg_price = ((db_holding.quantity * db_holding.averagePrice) + (payload.quantity * payload.price_per_share)) / new_quantity      

                db_holding.quantity = new_quantity
                db_holding.averagePrice = new_avg_price

            else:
                # new holding
                db_holding = Holding(
                    portfolioId=payload.portfolio_id,
                    ticker_id=payload.ticker_id,
                    quantity=payload.quantity,
                    averagePrice=payload.price_per_share
                )
                session.add(db_holding)
        
        elif payload.type == "SELL":
            if not db_holding:
                raise HTTPException(status_code=400, detail="No holding found to sell")
            
            if db_holding.quantity < payload.quantity:
                raise HTTPException(status_code=400, detail="Insufficient quantity to sell")
            
            new_quantity = db_holding.quantity - payload.quantity
            db_holding.quantity = new_quantity
            
            # delete if no more shares left
            if new_quantity == 0:
                await session.delete(db_holding)

        new_transaction = Transaction(
            portfolioId=payload.portfolio_id,
            ticker_id=payload.ticker_id,
            type=payload.type,
            quantity=payload.quantity,
            price=payload.price_per_share,
            total=total,
            timestamp=payload.timestamp
        )
        session.add(new_transaction)
        await session.commit()
        await session.refresh(new_transaction)
        
        return {"transaction_id": new_transaction.transactionId, "status": "success"}
    
    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")