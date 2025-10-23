from pydantic import BaseModel, ConfigDict

class PortfolioCreate(BaseModel):
    name: str
    description: str | None = None

class PortfolioOut(BaseModel):
    portfolioId: int
    userId: int
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)
