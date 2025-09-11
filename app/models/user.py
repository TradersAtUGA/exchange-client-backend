from sqlalchemy import Column, Integer, String
from app.models.base import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    userId = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(200), nullable=False)

    portfolios = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")