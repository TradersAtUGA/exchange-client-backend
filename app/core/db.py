import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Get connection string from env (docker-compose passes DATABASE_URL)
DATABASE_URL = os.environ["DATABASE_URL"]


# Engine: manages the connection pool to the MySQL db
engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True, 
)

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
