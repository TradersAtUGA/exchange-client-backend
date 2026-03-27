# app/core/market_simulator.py
import asyncio
import math
import random
import time
import logging
from dataclasses import dataclass, field
from typing import Callable, Awaitable
from decimal import Decimal

logger = logging.getLogger(__name__)


@dataclass
class TradeEvent:
    id: int
    symbol: str
    side: str          # "buy" | "sell"
    price: Decimal
    size: int
    timestamp: Decimal   # unix ms
    type: str          # "aggressive" | "passive"

    def to_dict(self) -> dict:
        return {
            "i":        self.id,
            "symbol":    self.symbol,
            "side":      self.side,
            "price":     self.price,
            "size":      self.size,
            "timestamp": self.timestamp,
            "type":      self.type,
        }


@dataclass
class OrderBookLevel:
    price: Decimal
    bid_size: int | None = None
    ask_size: int | None = None


class MarketSimulator:
    """
    Simulates a continuous order book and trade stream for a single symbol.
    Generates ~10 trades/sec with cosine-driven buy/sell momentum.
    Calls on_trade for every matched trade so the candle store and
    WebSocket broadcaster can consume it.
    """

    TICK = 0.25
    INTERVAL_MS = 100          # fire every 100ms
    LEVELS = 20                # order book depth each side

    def __init__(self, symbol: str, seed_price: Decimal = 100.0):
        self.symbol     = symbol
        self._trade_id  = 1
        self._task: asyncio.Task | None = None
        self._handlers: list[Callable[[TradeEvent], Awaitable[None]]] = []

        # Build initial order book around seed price
        mid = round(seed_price / self.TICK) * self.TICK
        self._levels: list[OrderBookLevel] = []
        for i in range(-self.LEVELS, self.LEVELS + 1):
            price = round((mid + i * self.TICK) * 100) / 100
            lvl   = OrderBookLevel(price=price)
            if i < 0:
                lvl.bid_size = random.randint(1, 20)
            elif i > 0:
                lvl.ask_size = random.randint(1, 20)
            self._levels.append(lvl)

    # ── Public API ────────────────────────────────────────────────────────────

    def add_handler(self, handler: Callable[[TradeEvent], Awaitable[None]]):
        self._handlers.append(handler)

    def remove_handler(self, handler: Callable[[TradeEvent], Awaitable[None]]):
        self._handlers.discard(handler) if hasattr(self._handlers, "discard") else None
        if handler in self._handlers:
            self._handlers.remove(handler)

    async def start(self):
        if self._task and not self._task.done():
            return
        self._task = asyncio.create_task(self._run(), name=f"sim-{self.symbol}")
        logger.info(f"MarketSimulator started for {self.symbol}")

    async def stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info(f"MarketSimulator stopped for {self.symbol}")

    # ── Simulation loop ───────────────────────────────────────────────────────

    async def _run(self):
        while True:
            try:
                trades = self._step()
                for trade in trades:
                    for handler in list(self._handlers):
                        try:
                            await handler(trade)
                        except Exception:
                            logger.exception("Trade handler error")
                await asyncio.sleep(self.INTERVAL_MS / 1000)
            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception(f"Simulator error for {self.symbol}")
                await asyncio.sleep(1)

    def _step(self) -> list[TradeEvent]:
        """Run one simulation tick. Returns a list of TradeEvents generated."""
        EPS     = 1e-6
        now_ms  = time.time() * 1000

        # Cosine momentum — smooth buy/sell wave
        period_ms = 6000
        buy_prob  = 0.5 + 0.3 * math.cos((now_ms / period_ms) * 2 * math.pi)
        side      = "bid" if random.random() < buy_prob else "ask"

        best_ask = next(
            (l for l in sorted(self._levels, key=lambda l: l.price)
             if l.ask_size and l.ask_size > 0), None
        )
        best_bid = next(
            (l for l in sorted(self._levels, key=lambda l: -l.price)
             if l.bid_size and l.bid_size > 0), None
        )

        center = (
            best_bid.price if best_bid and random.random() < 0.5
            else best_ask.price if best_ask
            else self._levels[len(self._levels) // 2].price
        )

        offset      = 0 if random.random() < 0.7 else random.randint(-1, 1)
        raw_price   = center - offset * self.TICK if side == "bid" else center + offset * self.TICK
        order_price = round(round(raw_price / self.TICK) * self.TICK, 2)
        order_size  = random.randint(1, 6)

        remaining = order_size
        trades: list[TradeEvent] = []

        if side == "bid":
            eligible = sorted(
                [l for l in self._levels if l.ask_size and l.ask_size > 0 and l.price <= order_price + EPS],
                key=lambda l: l.price,
            )
            for lvl in eligible:
                if remaining <= 0:
                    break
                filled    = min(lvl.ask_size, remaining)
                remaining -= filled
                lvl.ask_size = (lvl.ask_size - filled) or None
                trades.append(TradeEvent(
                    id=self._trade_id, symbol=self.symbol,
                    side="buy", price=lvl.price, size=filled,
                    timestamp=now_ms, type="aggressive",
                ))
                self._trade_id += 1

            if remaining > 0:
                lvl = next((l for l in self._levels if abs(l.price - order_price) < EPS), None)
                if lvl:
                    lvl.bid_size = (lvl.bid_size or 0) + remaining
                    trades.append(TradeEvent(
                        id=self._trade_id, symbol=self.symbol,
                        side="buy", price=order_price, size=remaining,
                        timestamp=now_ms, type="passive",
                    ))
                    self._trade_id += 1
        else:
            eligible = sorted(
                [l for l in self._levels if l.bid_size and l.bid_size > 0 and l.price >= order_price - EPS],
                key=lambda l: -l.price,
            )
            for lvl in eligible:
                if remaining <= 0:
                    break
                filled    = min(lvl.bid_size, remaining)
                remaining -= filled
                lvl.bid_size = (lvl.bid_size - filled) or None
                trades.append(TradeEvent(
                    id=self._trade_id, symbol=self.symbol,
                    side="sell", price=lvl.price, size=filled,
                    timestamp=now_ms, type="aggressive",
                ))
                self._trade_id += 1

            if remaining > 0:
                lvl = next((l for l in self._levels if abs(l.price - order_price) < EPS), None)
                if lvl:
                    lvl.ask_size = (lvl.ask_size or 0) + remaining
                    trades.append(TradeEvent(
                        id=self._trade_id, symbol=self.symbol,
                        side="sell", price=order_price, size=remaining,
                        timestamp=now_ms, type="passive",
                    ))
                    self._trade_id += 1

        # Occasionally replenish thin levels so the book doesn't drain
        self._replenish()
        return trades

    def _replenish(self):
        """Refill any side of the book that has gone thin."""
        for lvl in self._levels:
            best_ask = next(
                (l for l in sorted(self._levels, key=lambda l: l.price)
                 if l.ask_size and l.ask_size > 0), None
            )
            best_bid = next(
                (l for l in sorted(self._levels, key=lambda l: -l.price)
                 if l.bid_size and l.bid_size > 0), None
            )
            if best_ask and lvl.price > best_ask.price and not lvl.ask_size:
                if random.random() < 0.05:
                    lvl.ask_size = random.randint(1, 10)
            if best_bid and lvl.price < best_bid.price and not lvl.bid_size:
                if random.random() < 0.05:
                    lvl.bid_size = random.randint(1, 10)



_simulators: dict[str, MarketSimulator] = {}

SEED_PRICES = {
    "AAPL": 213.50, "MSFT": 415.25, "GOOGL": 172.80, "AMZN": 195.40,
    "TSLA": 248.75, "META": 582.10, "NVDA": 875.30, "JPM":  220.60,
    "V":    290.15, "JNJ":  155.90,
}


def get_simulator(symbol: str) -> MarketSimulator:
    """Get or create a simulator for the given symbol."""
    if symbol not in _simulators:
        seed = SEED_PRICES.get(symbol.upper(), 100.0)
        _simulators[symbol] = MarketSimulator(symbol=symbol.upper(), seed_price=seed)
    return _simulators[symbol]


async def start_all_simulators():
    """Start simulators for all known symbols at app startup."""
    for symbol in SEED_PRICES:
        sim = get_simulator(symbol)
        await sim.start()


async def stop_all_simulators():
    """Stop all simulators at app shutdown."""
    for sim in _simulators.values():
        await sim.stop()

