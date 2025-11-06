from pydantic import BaseModel, ConfigDict

class HoldingOut(BaseModel):
    holdingId: int
    portfolioId: int
    ticker_id: int
    quantity: float
    averagePrice: float

    model_config = ConfigDict(from_attributes=True)