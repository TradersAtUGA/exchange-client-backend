from fastapi import FastAPI
from app.routers import health, auth
from app.core.config import settings
from app.core.db import init_db


app = FastAPI(title=settings.PROJECT_NAME, debug=settings.DEBUG)

@app.on_event("startup")
async def startup_event():
    await init_db()

# include routers
app.include_router(health.router)
app.include_router(auth.router)

