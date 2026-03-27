# app/core/candle_store.py
"""
In-memory candle store.

Structure:
    _store[symbol][interval_ms][bucket_start_ms] = Candle

Candles are built incrementally — each incoming TradeEvent updates the
current bucket's OHLCV directly. Past buckets are sealed (isClosed=True)
and never mutated again. This means:
  - Zero re-derivation cost: no scanning raw trades
  - Unlimited history: a sealed candle is ~100 bytes regardless of trade count
  - All intervals updated simultaneously on every trade
"""

from __future__ import annotations
import time
import logging
from dataclasses import dataclass
from decimal import Decimal

logger = logging.getLogger(__name__)

# Intervals tracked for every symbol (ms)
INTERVAL_MS: list[int] = [60_000, 300_000, 1_800_000, 3_600_000, 86_400_000]  


@dataclass
class Candle:
    time:      int    # bucket start, unix ms
    open:      Decimal
    high:      Decimal
    low:       Decimal
    close:     Decimal
    volume:    int
    is_closed: bool

    def to_dict(self) -> dict:
        return {
            "time":     self.time,
            "open":     self.open,
            "high":     self.high,
            "low":      self.low,
            "close":    self.close,
            "volume":   self.volume,
            "isClosed": self.is_closed,
        }


# _store[symbol][interval_ms][bucket_ms] -> Candle
_store: dict[str, dict[int, dict[int, Candle]]] = {}

def _ensure_symbol(symbol: str):
    if symbol not in _store:
        _store[symbol] = {ms: {} for ms in INTERVAL_MS}


def ingest(symbol: str, price: Decimal, timestamp_ms: Decimal):
    """
    Ingest a single price tick into all intervals for a symbol.
    Called on every TradeEvent from the simulator or UDP listener.
    """
    _ensure_symbol(symbol)
    now_ms = int(timestamp_ms)

    for ms in INTERVAL_MS:
        current_bucket = (now_ms // ms) * ms
        interval_map   = _store[symbol][ms]

        # Seal any live candle that belongs to an old bucket
        for bucket_time, candle in list(interval_map.items()):
            if not candle.is_closed and bucket_time != current_bucket:
                candle.is_closed = True

        # Update or create the current bucket's candle
        if current_bucket in interval_map:
            c = interval_map[current_bucket]
            c.close  = price
            c.high   = max(c.high, price)
            c.low    = min(c.low, price)
            c.volume += 1
        else:
            interval_map[current_bucket] = Candle(
                time=current_bucket,
                open=price, high=price, low=price, close=price,
                volume=1, is_closed=False,
            )


def get_candles(symbol: str, interval_ms: int, limit: int = 500) -> list[dict]:
    """
    Return the most recent `limit` candles for a symbol/interval,
    oldest first (ready to send as snapshot on WebSocket connect).
    """
    _ensure_symbol(symbol)
    interval_map = _store[symbol].get(interval_ms, {})
    sorted_candles = sorted(interval_map.values(), key=lambda c: c.time)

    return [c.to_dict() for c in sorted_candles[-limit:]]


def get_latest_candle(symbol: str, interval_ms: int) -> dict | None:
    """Return the current live (unsealed) candle for a symbol/interval."""
    _ensure_symbol(symbol)
    interval_map = _store[symbol].get(interval_ms, {})
    now_ms         = int(time.time() * 1000)
    current_bucket = (now_ms // interval_ms) * interval_ms
    candle = interval_map.get(current_bucket)
    return candle.to_dict() if candle else None