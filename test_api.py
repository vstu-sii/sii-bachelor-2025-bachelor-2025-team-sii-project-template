"""
Тестовый клиент для проверки API без запуска сервера.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from api.main import create_application

# Создаём тестовое приложение
app = create_application()
client = TestClient(app)

def test_api_endpoints():
    """Тестирование основных эндпоинтов API"""
    
    print("🧪 Тестирование Cooking Assistant API...")
    
    # 1. Проверка корневого эндпоинта
    print("1. Тестирование корневого эндпоинта...")
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Cooking Assistant API"
    print("   ✅ Корневой эндпоинт работает")
    
    # 2. Проверка health check
    print("2. Тестирование health check...")
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("   ✅ Health check работает")
    
    # 3. Проверка документации
    print("3. Тестирование документации...")
    response = client.get("/api/docs")
    assert response.status_code == 200
    print("   ✅ Swagger документация доступна")
    
    # 4. Проверка схемы OpenAPI
    print("4. Тестирование OpenAPI схемы...")
    response = client.get("/api/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    print("   ✅ OpenAPI схема доступна")
    
    # 5. Проверка эндпоинтов аутентификации (без авторизации)
    print("5. Тестирование эндпоинтов аутентификации...")
    
    # Регистрация (должна вернуть 400 т.к. нет данных)
    response = client.post("/api/auth/register", json={})
    assert response.status_code == 422  # Validation error
    print("   ✅ Эндпоинт регистрации отвечает")
    
    # Логин (должен вернуть 422)
    response = client.post("/api/auth/login", data={"username": "", "password": ""})
    assert response.status_code == 422
    print("   ✅ Эндпоинт логина отвечает")
    
    # 6. Проверка эндпоинтов блюд (должны требовать авторизацию)
    print("6. Тестирование защищённых эндпоинтов...")
    
    # Попытка получить блюда без авторизации
    response = client.get("/api/dishes/")
    assert response.status_code == 401 or response.status_code == 403
    print("   ✅ Эндпоинты защищены авторизацией")
    
    print("\n🎉 Все тесты пройдены успешно!")
    print("\n📋 Доступные эндпоинты:")
    for route in app.routes:
        if hasattr(route, "methods"):
            methods = ",".join(route.methods)
            path = route.path
            print(f"   {methods:10} {path}")
    
    return True

if __name__ == "__main__":
    try:
        success = test_api_endpoints()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
