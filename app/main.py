from fastapi import FastAPI
from app.routers import health, auth, users, portfolios, transactions, ticker
from app.core.config import settings
from app.core.db import init_db
from app.core.udp_listener import init_udp_listener, shutdown_udp_listener, get_udp_listener
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

async def print_messages(data: bytes, addr: tuple):
    print(f"Received message from {addr}: {data.decode()}")

@app.on_event("startup")
async def startup_event():
    await init_db()
    await init_udp_listener(host=settings.UDP_HOST, port=settings.UDP_PORT)
    
    # Set the message handler
    listener = get_udp_listener()
    if listener:
        listener.set_message_handler(print_messages)



@app.on_event("shutdown")
async def shutdown_event():
    await shutdown_udp_listener()

# include routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(portfolios.router)
app.include_router(transactions.router)
app.include_router(ticker.router)