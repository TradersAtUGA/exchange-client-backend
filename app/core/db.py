import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from app.models.base import Base
from app.models.ticker import Ticker
import asyncio



# Get connection string from env (docker-compose passes DATABASE_URL)
DATABASE_URL = os.environ["DATABASE_URL"]


# Engine: manages the connection pool to the MySQL db
engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True, 
)

async def wait_for_db(max_retries: int = 10, delay: int = 3):
    for attempt in range(1, max_retries + 1):
        try:
            async with engine.connect() as conn:
                await conn.execute("SELECT 1")
                return
        except Exception:
            if attempt == max_retries:
                raise TimeoutError("Timed out waiting for the database to be available")
            await asyncio.sleep(delay)

# Session factory: callable used to create session objects bound to the engine
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)

# Dependency to get a session for FastAPI routes
async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# Sample ticker data
SEED_TICKERS = [
    {"symbol": "AAPL", "name": "Apple Inc."},
    {"symbol": "MSFT", "name": "Microsoft Corporation"},
    {"symbol": "GOOGL", "name": "Alphabet Inc."},
    {"symbol": "AMZN", "name": "Amazon.com Inc."},
    {"symbol": "TSLA", "name": "Tesla Inc."},
    {"symbol": "META", "name": "Meta Platforms Inc."},
    {"symbol": "NVDA", "name": "NVIDIA Corporation"},
    {"symbol": "JPM", "name": "JPMorgan Chase & Co."},
    {"symbol": "V", "name": "Visa Inc."},
    {"symbol": "JNJ", "name": "Johnson & Johnson"},
]

# Initialize database tables
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # add ticker data
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Ticker))
        existing = result.scalars().all()
        
        if not existing:
            for ticker_data in SEED_TICKERS:
                ticker = Ticker(symbol=ticker_data["symbol"], name=ticker_data["name"])
                session.add(ticker)
            
            await session.commit()