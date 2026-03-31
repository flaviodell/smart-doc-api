from fastapi import FastAPI
from .core.database import engine, Base
from .api.endpoints import router as ai_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Doc API")

app.include_router(ai_router, prefix="/ai", tags=["AI Operations"])

@app.get("/")
def read_root():
    return {"message": "Smart Doc API is up and running!"}