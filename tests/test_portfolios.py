import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_user_portfolios_empty(client: AsyncClient):
    response = await client.get("/users/portfolios")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_portfolio(client: AsyncClient):
    response = await client.post("/users/portfolios", json={
        "name": "Growth Portfolio",
        "description": "Long-term holdings"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Growth Portfolio"
    assert "portfolioId" in data


@pytest.mark.asyncio
async def test_get_portfolio_holdings_not_found(client: AsyncClient):
    response = await client.get("/portfolios/9999/holdings")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_portfolio_holdings_empty(client: AsyncClient, seeded_portfolio):
    response = await client.get(f"/portfolios/{seeded_portfolio.portfolioId}/holdings")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_portfolio_transactions_empty(client: AsyncClient, seeded_portfolio):
    response = await client.get(f"/portfolios/{seeded_portfolio.portfolioId}/transactions")
    assert response.status_code == 200
    assert response.json() == []