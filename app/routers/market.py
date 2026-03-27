# app/routers/market.py
"""
WebSocket market data endpoint.

Connect: ws://host/market/ws/{symbol}

On connect the client immediately receives:
  { "type": "snapshot", "trades": [...last 100 trades], "candles": { "60000": [...], ... } }

Then every trade event is streamed as:
  { "type": "trade", "data": { id, symbol, side, price, size, timestamp, type } }

"""

import json
import logging
from collections import deque
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.market_simulator import get_simulator, TradeEvent
from app.core import candle_store
from app.core.candle_store import INTERVAL_MS

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/market", tags=["market"])

# Recent trade buffer per symbol — keeps last 100 trades for snapshot on connect
_trade_buffer: dict[str, deque[dict]] = {}
TRADE_BUFFER_SIZE = 100


def _get_buffer(symbol: str) -> deque[dict]:
    if symbol not in _trade_buffer:
        _trade_buffer[symbol] = deque(maxlen=TRADE_BUFFER_SIZE)
    return _trade_buffer[symbol]


class ConnectionManager:
    """Tracks active WebSocket connections per symbol."""

    def __init__(self):
        # symbol -> set of WebSocket connections
        self._connections: dict[str, set[WebSocket]] = {}

    def connect(self, symbol: str, ws: WebSocket):
        self._connections.setdefault(symbol, set()).add(ws)
        logger.info(f"WS connected [{symbol}] — total: {len(self._connections[symbol])}")

    def disconnect(self, symbol: str, ws: WebSocket):
        self._connections.get(symbol, set()).discard(ws)
        logger.info(f"WS disconnected [{symbol}] — total: {len(self._connections.get(symbol, set()))}")


    async def broadcast(self, symbol: str, message: str):
        dead = set()
        connections = list(self._connections.get(symbol, set()))
        
        async def send(ws):
            try:
                await ws.send_text(message)
            except Exception:
                dead.add(ws)
        
        await asyncio.gather(*[send(ws) for ws in connections])
        
        for ws in dead:
            self.disconnect(symbol, ws)


manager = ConnectionManager()


async def _handle_trade(trade: TradeEvent):
    symbol = trade.symbol

    candle_store.ingest(symbol, trade.price, trade.timestamp)
    _get_buffer(symbol).append(trade.to_dict())

    # Broadcast the trade
    await manager.broadcast(symbol, json.dumps({
        "type": "trade",
        "data": trade.to_dict()
    }))

    # Broadcast updated candle for every interval
    for interval in INTERVAL_MS:
        candle = candle_store.get_latest_candle(symbol, interval)
        if candle:
            await manager.broadcast(symbol, json.dumps({
                "type": "candle",
                "interval": interval,
                "data": candle
            }))

_registered_symbols: set[str] = set()

# get data from simulator -> replace with c++ engine

@router.websocket("/ws/{symbol}")
async def market_ws(websocket: WebSocket, symbol: str):
    symbol = symbol.upper()
    await websocket.accept()
    manager.connect(symbol, websocket)

    sim = get_simulator(symbol)

    # Only register the handler once per symbol
    if symbol not in _registered_symbols:
        sim.add_handler(_handle_trade)
        _registered_symbols.add(symbol)

    try:
        snapshot = {
            "type": "snapshot",
            "trades": list(_get_buffer(symbol)),
            "candles": {
                str(interval_ms): candle_store.get_candles(symbol, interval_ms)
                for interval_ms in candle_store.INTERVAL_MS
            },
        }

        await websocket.send_text(json.dumps(snapshot))
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(symbol, websocket)
        # DO NOT remove handler here — other clients still need it



