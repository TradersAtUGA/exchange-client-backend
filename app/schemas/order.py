from pydantic import BaseModel, ConfigDict
from enum import Enum
from decimal import Decimal
from datetime import datetime
from typing import Optional

class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(str, Enum):
    LIMIT = "limit"
    MARKET = "market"

class TimeInForce(str, Enum):
    GTC = "GTC"
    IOC = "IOC"
    DAY = "DAY"

class OrderIn(BaseModel):
    side: Side
    orderType: OrderType
    timeInForce: TimeInForce
    ticker: str
    qty: Decimal
    price: Optional[Decimal] = None

class OrderOut(BaseModel):
    side: Side
    orderType: OrderType
    timeInForce: TimeInForce
    ticker: str
    qty: Decimal
    price: Optional[Decimal] = None
    orderId: int
    timePlaced: datetime

    model_config = ConfigDict(from_attributes=True)
