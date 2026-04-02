from fastapi import FastAPI
from .core.database import engine, Base
from .core.logging import setup_logging
from .api.endpoints import router as ai_router

setup_logging()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Doc API")

app.include_router(ai_router, prefix="/ai", tags=["AI Operations"])

@app.get("/")
def read_root():
    return {"message": "Smart Doc API is up and running!"}

@app.get("/health")
def health():
    return {"status": "ok"}