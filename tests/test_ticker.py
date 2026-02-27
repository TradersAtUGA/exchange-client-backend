import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_tickers_empty(client: AsyncClient):
    response = await client.get("/ticker/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_tickers_returns_seeded(client: AsyncClient, seeded_ticker):
    response = await client.get("/ticker/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["symbol"] == "AAPL"


@pytest.mark.asyncio
async def test_get_ticker_by_id(client: AsyncClient, seeded_ticker):
    response = await client.get(f"/ticker/{seeded_ticker.ticker_id}")
    assert response.status_code == 200
    assert response.json()["symbol"] == "AAPL"


@pytest.mark.asyncio
async def test_get_ticker_by_id_not_found(client: AsyncClient):
    response = await client.get("/ticker/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_ticker_by_symbol(client: AsyncClient, seeded_ticker):
    response = await client.get("/ticker/symbol/AAPL")
    assert response.status_code == 200
    assert response.json()["name"] == "Apple Inc."


@pytest.mark.asyncio
async def test_get_ticker_by_symbol_not_found(client: AsyncClient, seeded_ticker):
    response = await client.get("/ticker/symbol/FAKE")
    assert response.status_code == 404