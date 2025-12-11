from fastapi import FastAPI
from backend.routers import ai

app = FastAPI(title="AI Pitch Deck Generator")
app.include_router(ai.router)
