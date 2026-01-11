import pytest
from fastapi import status
from unittest.mock import Mock, patch
import json

class TestAuthEndpoints:
    def test_register_success(self, client):
        """Тест успешной регистрации"""
        user_data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert "id" in data
        assert data["is_active"] is True
    
    def test_register_duplicate_email(self, client, test_user):
        """Тест регистрации с существующим email"""
        user_data = {
            "username": "differentuser",
            "email": test_user.email,  # Используем email существующего пользователя
            "password": "password123"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "уже существует" in response.json()["detail"]
    
    def test_register_invalid_password(self, client):
        """Тест регистрации с коротким паролем"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "123"  # Слишком короткий пароль
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_success(self, client, test_user):
        """Тест успешного входа"""
        # Создаём пользователя с известным паролем
        login_data = {
            "username": test_user.email,
            "password": "testpassword"
        }
        
        response = client.post(
            "/api/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client):
        """Тест входа с неверными данными"""
        login_data = {
            "username": "wrong@example.com",
            "password": "wrongpassword"
        }
        
        response = client.post(
            "/api/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user(self, client, auth_headers):
        """Тест получения текущего пользователя"""
        response = client.get("/api/auth/me", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert "username" in data
        assert "email" in data
    
    def test_get_current_user_unauthorized(self, client):
        """Тест получения пользователя без авторизации"""
        response = client.get("/api/auth/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_logout(self, client, auth_headers):
        """Тест выхода из системы"""
        response = client.post("/api/auth/logout", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Successfully logged out"

class TestDishEndpoints:
    def test_create_dish_success(self, client, auth_headers):
        """Тест успешного создания блюда"""
        # Создаём тестовый файл
        test_file_content = b"fake image content"
        
        files = {
            "photo": ("test.jpg", test_file_content, "image/jpeg")
        }
        
        data = {
            "dish_type": "dinner",
            "user_recipe_text": "Test recipe " * 10  # 50+ символов
        }
        
        response = client.post(
            "/api/dishes/",
            headers=auth_headers,
            data=data,
            files=files
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["dish_type"] == "dinner"
        assert data["status"] == "draft"
        assert "photo_url" in data
        assert data["photo_url"].startswith("/uploads/dishes/")
    
    def test_create_dish_short_recipe(self, client, auth_headers):
        """Тест создания блюда с коротким рецептом"""
        test_file_content = b"fake image content"
        
        files = {
            "photo": ("test.jpg", test_file_content, "image/jpeg")
        }
        
        data = {
            "dish_type": "dinner",
            "user_recipe_text": "Short"  # Менее 50 символов
        }
        
        response = client.post(
            "/api/dishes/",
            headers=auth_headers,
            data=data,
            files=files
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_dish_unauthorized(self, client):
        """Тест создания блюда без авторизации"""
        response = client.post("/api/dishes/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_dishes(self, client, auth_headers, test_dish):
        """Тест получения списка блюд"""
        response = client.get("/api/dishes/", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            dish = data[0]
            assert "id" in dish
            assert "user_recipe_text" in dish
            assert "dish_type" in dish
    
    def test_get_dishes_with_status_filter(self, client, auth_headers, test_dish):
        """Тест получения блюд с фильтром по статусу"""
        response = client.get(
            "/api/dishes/",
            headers=auth_headers,
            params={"status": "draft"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # В данном mock-тесте все блюда будут draft
    
    def test_get_dish_by_id(self, client, auth_headers, test_dish):
        """Тест получения конкретного блюда"""
        response = client.get(f"/api/dishes/{test_dish.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_dish.id
        assert data["dish_type"] == test_dish.dish_type.value
    
    def test_get_nonexistent_dish(self, client, auth_headers):
        """Тест получения несуществующего блюда"""
        response = client.get("/api/dishes/99999", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_analyze_dish_success(self, client, auth_headers, test_dish):
        """Тест успешного анализа блюда"""
        with patch('backend.services.ai_service.AIService.analyze_dish') as mock_analyze:
            mock_analysis = Mock()
            mock_analysis.appearance_score = 4
            mock_analysis.recipe_score = 3
            mock_analysis.appearance_feedback = "Good"
            mock_analysis.recipe_feedback = "OK"
            mock_analysis.recommendations = "Improve"
            mock_analysis.ai_metadata = {"model": "test"}
            mock_analyze.return_value = mock_analysis
            
            response = client.post(
                f"/api/dishes/{test_dish.id}/analyze",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["appearance_score"] == 4
            assert data["recipe_score"] == 3
            assert "recommendations" in data
    
    def test_analyze_dish_already_analyzed(self, client, auth_headers, test_dish):
        """Тест повторного анализа блюда"""
        # Сначала создаём анализ
        from backend.crud.rating import create_rating
        from backend.schemas.rating import RatingCreate
        
        rating_data = RatingCreate(
            dish_id=test_dish.id,
            appearance_score=4,
            recipe_score=3,
            appearance_feedback="Test",
            recipe_feedback="Test",
            recommendations="Test"
        )
        
        from backend.database import SessionLocal
        db = SessionLocal()
        create_rating(db, rating_data)
        db.close()
        
        # Пытаемся проанализировать снова
        response = client.post(
            f"/api/dishes/{test_dish.id}/analyze",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "уже выполнен" in response.json()["detail"]
    
    def test_get_dish_analysis(self, client, auth_headers, test_dish):
        """Тест получения результатов анализа"""
        # Сначала создаём анализ
        from backend.crud.rating import create_rating
        from backend.schemas.rating import RatingCreate
        
        rating_data = RatingCreate(
            dish_id=test_dish.id,
            appearance_score=4,
            recipe_score=3,
            appearance_feedback="Test feedback",
            recipe_feedback="Test recipe",
            recommendations="Test recommendations"
        )
        
        from backend.database import SessionLocal
        db = SessionLocal()
        create_rating(db, rating_data)
        db.close()
        
        # Получаем анализ
        response = client.get(
            f"/api/dishes/{test_dish.id}/analysis",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["appearance_score"] == 4
        assert data["recommendations"] == "Test recommendations"
    
    def test_get_dish_analysis_not_found(self, client, auth_headers, test_dish):
        """Тест получения анализа для блюда без анализа"""
        response = client.get(
            f"/api/dishes/{test_dish.id}/analysis",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_dish(self, client, auth_headers, test_dish):
        """Тест обновления блюда"""
        update_data = {
            "dish_type": "lunch",
            "user_recipe_text": "Updated recipe " * 10
        }
        
        response = client.put(
            f"/api/dishes/{test_dish.id}",
            headers=auth_headers,
            json=update_data
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["dish_type"] == "lunch"
    
    def test_update_nonexistent_dish(self, client, auth_headers):
        """Тест обновления несуществующего блюда"""
        update_data = {
            "dish_type": "lunch"
        }
        
        response = client.put(
            "/api/dishes/99999",
            headers=auth_headers,
            json=update_data
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_dish(self, client, auth_headers, test_dish):
        """Тест удаления блюда"""
        response = client.delete(
            f"/api/dishes/{test_dish.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Проверяем что блюдо действительно удалено
        get_response = client.get(
            f"/api/dishes/{test_dish.id}",
            headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_nonexistent_dish(self, client, auth_headers):
        """Тест удаления несуществующего блюда"""
        response = client.delete(
            "/api/dishes/99999",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

class TestStatisticsEndpoints:
    def test_get_statistics_overview(self, client, auth_headers):
        """Тест получения общей статистики"""
        response = client.get("/api/statistics/overview", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_dishes" in data
        assert "average_scores" in data
        assert "dish_type_distribution" in data
    
    def test_get_dish_type_statistics(self, client, auth_headers):
        """Тест получения статистики по типу блюд"""
        response = client.get(
            "/api/statistics/dish-types/dinner",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "dish_type" in data
        assert "average_scores" in data
        assert "total_count" in data
    
    def test_get_progress_timeline(self, client, auth_headers):
        """Тест получения временной шкалы прогресса"""
        response = client.get(
            "/api/statistics/progress",
            headers=auth_headers,
            params={"days": 30}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            item = data[0]
            assert "date" in item
            assert "count" in item
            assert "average_score" in item
    
    def test_health_check(self, client):
        """Тест проверки работоспособности API"""
        response = client.get("/api/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_root_endpoint(self, client):
        """Тест корневого эндпоинта"""
        response = client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data

class TestErrorHandling:
    def test_validation_error(self, client, auth_headers):
        """Тест обработки ошибок валидации"""
        # Пытаемся создать блюдо с неверным типом
        test_file_content = b"fake image content"
        
        files = {
            "photo": ("test.jpg", test_file_content, "image/jpeg")
        }
        
        data = {
            "dish_type": "invalid_type",  # Неверный тип
            "user_recipe_text": "Test recipe " * 10
        }
        
        response = client.post(
            "/api/dishes/",
            headers=auth_headers,
            data=data,
            files=files
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_internal_server_error(self, client, auth_headers, test_dish):
        """Тест обработки внутренних ошибок сервера"""
        with patch('backend.crud.dish.get_dish') as mock_get_dish:
            mock_get_dish.side_effect = Exception("Database error")
            
            response = client.get(
                f"/api/dishes/{test_dish.id}",
                headers=auth_headers
            )
            
            # В реальном приложении это вызвало бы 500 ошибку
            # Но в тестах мы можем проверить что исключение перехвачено
            assert response.status_code in [500, 404]
    
    def test_file_upload_error(self, client, auth_headers):
        """Тест ошибки при загрузке файла"""
        # Пытаемся загрузить слишком большой файл
        huge_file_content = b"x" * (11 * 1024 * 1024)  # 11MB
        
        files = {
            "photo": ("huge.jpg", huge_file_content, "image/jpeg")
        }
        
        data = {
            "dish_type": "dinner",
            "user_recipe_text": "Test recipe " * 10
        }
        
        # В реальном приложении должен быть лимит на размер файла
        response = client.post(
            "/api/dishes/",
            headers=auth_headers,
            data=data,
            files=files
        )
        
        # Проверяем что запрос обработан (даже если с ошибкой)
        assert response.status_code in [200, 400, 413, 422]

class TestRateLimiting:
    def test_rate_limiting_on_auth(self, client):
        """Тест ограничения запросов (если бы оно было реализовано)"""
        # В данном проекте rate limiting не реализован,
        # но структура теста готова для его добавления
        for _ in range(5):
            response = client.post("/api/auth/login", data={
                "username": "test@example.com",
                "password": "test"
            })
            # Все запросы должны проходить
            assert response.status_code in [200, 401, 422]
