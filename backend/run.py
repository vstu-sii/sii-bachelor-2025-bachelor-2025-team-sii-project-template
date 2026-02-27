#!/usr/bin/env python3
"""
Скрипт для запуска FastAPI приложения.
"""
import uvicorn
import os

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    print(f"🚀 Запуск Cooking Assistant API на http://{host}:{port}")
    print(f"📚 Документация: http://{host}:{port}/api/docs")
    print(f"🔄 Режим перезагрузки: {reload}")
    
    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
