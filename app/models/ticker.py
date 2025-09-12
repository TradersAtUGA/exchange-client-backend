from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

class Ticker(Base):
    __tablename__ = "tickers"

    ticker_id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    holdings = relationship("Holding", back_populates="ticker", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="ticker", cascade="all, delete-orphan")