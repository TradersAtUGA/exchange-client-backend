import pytest
from httpx import AsyncClient
from datetime import datetime


PAYLOAD = {
    "user_id": 1,          
    "portfolio_id": 1,
    "ticker_id": 1,
    "timestamp": datetime.utcnow().isoformat(),
}

@pytest.mark.asyncio
async def test_buy_creates_holding(client: AsyncClient, seeded_portfolio):
    response = await client.post("/transactions/", json={**PAYLOAD, "price_per_share": 150, "quantity": 10, "type": "BUY"})
    assert response.status_code == 201
    assert response.json()["status"] == "success"

    # Verify holding was created
    holdings = await client.get(f"/portfolios/{seeded_portfolio.portfolioId}/holdings")
    assert holdings.status_code == 200
    data = holdings.json()
    assert len(data) == 1
    assert data[0]["quantity"] == 10
    assert data[0]["averagePrice"] == 150.00

async def test_buy_updates_average_price(client: AsyncClient, seeded_portfolio):
    await client.post("/transactions/", json={**PAYLOAD, "price_per_share": 100.00, "quantity": 10, "type": "BUY"})
    await client.post("/transactions/", json={**PAYLOAD, "price_per_share": 200.00, "quantity": 10, "type": "BUY"})

    holdings = await client.get("/portfolios/1/holdings")

    data = holdings.json()
    assert data[0]["averagePrice"] == 150.00
    assert data[0]["quantity"] == 20

@pytest.mark.asyncio
async def test_sell_without_holding_returns_400(client: AsyncClient, seeded_portfolio):
    response = await client.post("/transactions/", json={**PAYLOAD, "price_per_share": 100.00, "quantity": 10, "type": "SELL"})
    assert response.status_code == 400
    assert "No holding found to sell" in response.json()["detail"]


@pytest.mark.asyncio
async def test_sell_insufficient_quantity_returns_400(client: AsyncClient, seeded_portfolio):
    await client.post("/transactions/", json={**PAYLOAD, "price_per_share": 100.00, "quantity": 5, "type":"BUY"})

    response = await client.post("/transactions/", json={**PAYLOAD, "price_per_share": 100.00, "quantity": 10, "type": "SELL"})

    assert response.status_code == 400
    assert "Insufficient" in response.json()["detail"]


@pytest.mark.asyncio
async def test_sell_removes_holding_when_quantity_zero(client: AsyncClient, seeded_portfolio):
    await client.post("/transactions/", json={**PAYLOAD,"price_per_share": 100.00, "quantity": 10, "type": "BUY"})
    response = await client.post("/transactions/", json={**PAYLOAD, "price_per_share": 100.00, "quantity": 10, "type": "SELL"})
    assert response.status_code == 201

    holdings = await client.get("/portfolios/1/holdings")
    assert holdings.json() == []


@pytest.mark.asyncio
async def test_transaction_invalid_portfolio_returns_404(client: AsyncClient, seeded_portfolio):
    response = await client.post("/transactions/", json={**PAYLOAD, "price_per_share": 100.00, "quantity":10, "portfolio_id": 9999, "type": "BUY"})
    assert response.status_code == 404