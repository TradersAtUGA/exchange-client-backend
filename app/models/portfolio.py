from sqlalchemy import Column, Integer, String, ForeignKey
from app.models.base import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class Portfolio(Base):
    __tablename__ = "portfolios"

    portfolioId = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey("users.userId"), nullable=False)
    name = Column(String(100), default="My Portfolio")
    description = Column(String(255), nullable=True)

    user = relationship("User", back_populates="portfolios")
    holdings = relationship("Holding", back_populates="portfolio", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="portfolio", cascade="all, delete-orphan")