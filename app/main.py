from fastapi import FastAPI
from .core.database import engine, Base

# Crea le tabelle nel DB (se non esistono)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Doc API")

@app.get("/")
def read_root():
    return {"message": "Smart Doc API is up and running!"}