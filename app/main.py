from fastapi import FastAPI
from app.routers import health, users
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME, debug=settings.DEBUG)

# include routers
app.include_router(health.router)
