from sqlalchemy import Column, Integer, ForeignKey, DECIMAL, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import enum

class TransactionType(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"

class Transaction(Base):
    __tablename__ = "transactions"

    transactionId = Column(Integer, primary_key=True, index=True)
    portfolioId = Column(Integer, ForeignKey("portfolios.portfolioId"), nullable=False)
    ticker_id = Column(Integer, ForeignKey("tickers.ticker_id"), nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    quantity = Column(DECIMAL(20, 8), nullable=False)
    price = Column(DECIMAL(20, 8), nullable=False)
    total = Column(DECIMAL(20, 8), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    portfolio = relationship("Portfolio", back_populates="transactions")
    ticker = relationship("Ticker", back_populates="transactions")