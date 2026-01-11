from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from datetime import datetime

from .routes import auth, dishes, statistics, users, upload

def create_application() -> FastAPI:
    """Создание и настройка FastAPI приложения"""
    
    app = FastAPI(
        title="Cooking Assistant API",
        description="API для умного помощника в готовке с AI-анализом блюд",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )
    
    # Настройка CORS
    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"]
    )
    
    # Подключаем роутеры
    app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(users.router, prefix="/api/users", tags=["Users"])
    app.include_router(dishes.router, prefix="/api/dishes", tags=["Dishes"])
    app.include_router(statistics.router, prefix="/api/statistics", tags=["Statistics"])
    app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
    
    # Статические файлы
    os.makedirs("uploads", exist_ok=True)
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
    
    # Health check
    @app.get("/api/health")
    async def health_check():
        return {
            "status": "healthy",
            "service": "cooking-assistant-api",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat()
        }
    
    # Информация о API
    @app.get("/")
    async def root():
        return {
            "message": "Cooking Assistant API",
            "version": "1.0.0",
            "docs": "/api/docs",
            "endpoints": {
                "auth": "/api/auth",
                "users": "/api/users",
                "dishes": "/api/dishes",
                "statistics": "/api/statistics",
                "upload": "/api/upload"
            }
        }
    
    return app

# Создаём экземпляр приложения
app = create_application()
