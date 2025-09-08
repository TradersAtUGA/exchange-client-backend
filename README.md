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