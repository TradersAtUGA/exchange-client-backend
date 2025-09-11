from sqlalchemy import Column, Integer, ForeignKey, DECIMAL, DateTime, UniqueConstraint
from app.models.base import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class Holding(Base):
    __tablename__ = "holdings"
    __table_args__ = (UniqueConstraint('portfolioId', 'ticker_id', name='uq_portfolio_asset'),)

    holdingId = Column(Integer, primary_key=True, index=True)
    portfolioId = Column(Integer, ForeignKey("portfolios.portfolioId"), nullable=False)
    ticker_id = Column(Integer, ForeignKey("tickers.ticker_id"), nullable=False)
    quantity = Column(DECIMAL(20, 8), default=0)
    averagePrice = Column(DECIMAL(20, 8), default=0)

    portfolio = relationship("Portfolio", back_populates="holdings")
    ticker = relationship("Ticker", back_populates="holdings")