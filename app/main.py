from fastapi import FastAPI

app = FastAPI(title="Exchange Client Backend")

@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}
