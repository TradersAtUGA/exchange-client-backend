from fastapi import FastAPI
from app.routers import health, auth, users
from app.core.config import settings
from app.core.db import init_db
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title=settings.PROJECT_NAME, debug=settings.DEBUG)


@app.on_event("startup")
async def startup_event():
    await init_db()

# include routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)

