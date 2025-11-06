from pydantic import BaseModel, Field, ConfigDict
from typing import Literal
import datetime
from app.models.transaction import TransactionType

class TransactionPayload(BaseModel):
    user_id: int
    portfolio_id: int
    ticker_id: int
    type: Literal["BUY", "SELL"]
    price_per_share: float = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    timestamp: datetime.datetime

class TransactionOut(BaseModel):
    transactionId: int
    portfolioId: int
    ticker_id: int
    type: TransactionType
    quantity: float
    price: float
    total: float
    timestamp: datetime.datetime

    model_config = ConfigDict(from_attributes=True)