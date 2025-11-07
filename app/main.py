from fastapi import FastAPI
from app.routers import health, auth, users, portfolios, transactions
from app.core.config import settings
from app.core.db import init_db
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title=settings.PROJECT_NAME, debug=settings.DEBUG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    await init_db()

# include routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(portfolios.router)
app.include_router(transactions.router)