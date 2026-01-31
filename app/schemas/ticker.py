from pydantic import BaseModel, ConfigDict

class TickerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    ticker_id: int
    symbol: str
    name: str