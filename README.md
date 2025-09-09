# Exchange Client Backend 

A lightweight, high-performance backend for connecting to market exchanges. Handles real-time data streaming, order execution, and account management with robust error handling and efficient API integration. Designed for scalability, reliability, and ease of integration into trading systems.

### Installation

```bash
# Clone the repository
git clone https://github.com/<your-org>/exchange-client-backend.git
cd exchange-client-backend

# Build images and start services (FastAPI + MySQL)
docker compose up --build

# (Optional) Run in background (detached mode)
docker compose up -d
```

### Project Structure
app/
  core/         # Configuration & infrastructure (settings, DB session, security)
  models/       # SQLAlchemy ORM models (database tables)
  routers/      # API route definitions (FastAPI APIRouter)
  schemas/      # Pydantic models for requests & responses
  main.py       # FastAPI entrypoint

.env            # Environment variables (not committed)
docker-compose.yml
Dockerfile
requirements.txt
README.md
