import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.models.base import Base
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

# Initialize database tables
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)