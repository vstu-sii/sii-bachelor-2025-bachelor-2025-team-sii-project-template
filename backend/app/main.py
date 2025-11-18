# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import ai  # 👈 إضافة مهمّة

# Создаём экземпляр FastAPI-приложения
app = FastAPI(
    title="Auto-Flashcards API",
    description="MVP прототип backend-сервиса для проекта Auto-Flashcards (роль: Fullstack)",
    version="0.1.0",
)

# Настройка CORS (минимальная для разработки с фронтендом на http://localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
async def health_check() -> dict:
    """
    Простой health-check эндпоинт.
    Нужен, чтобы быстро проверить, что backend запустился и отвечает.
    """
    return {"status": "ok"}


app.include_router(ai.router, prefix="/ai", tags=["ai"])
