import pytest
from unittest.mock import Mock, patch
from backend.services.ai_service import AIService
from backend.schemas.dish import DishAnalysisRequest, DishType
from backend.schemas.rating import AnalysisResult

class TestAIService:
    def test_analyze_dish_returns_correct_structure(self):
        """Тест что анализ возвращает корректную структуру"""
        request = DishAnalysisRequest(
            photo_url="/uploads/test.jpg",
            user_recipe_text="Test recipe",
            dish_type=DishType.DINNER
        )
        
        result = AIService.analyze_dish(request)
        
        assert isinstance(result, AnalysisResult)
        assert hasattr(result, 'appearance_score')
        assert hasattr(result, 'recipe_score')
        assert hasattr(result, 'appearance_feedback')
        assert hasattr(result, 'recipe_feedback')
        assert hasattr(result, 'recommendations')
        assert hasattr(result, 'ai_metadata')
    
    def test_analyze_dish_score_range(self):
        """Тест что оценки находятся в допустимом диапазоне"""
        request = DishAnalysisRequest(
            photo_url="/uploads/test.jpg",
            user_recipe_text="Test recipe",
            dish_type=DishType.DINNER
        )
        
        # Запускаем анализ несколько раз для проверки диапазона
        for _ in range(10):
            result = AIService.analyze_dish(request)
            
            assert 1 <= result.appearance_score <= 5
            assert 1 <= result.recipe_score <= 5
            
            # Проверяем что оценки - целые числа
            assert isinstance(result.appearance_score, int)
            assert isinstance(result.recipe_score, int)
    
    def test_analyze_dish_contains_feedback(self):
        """Тест что анализ содержит текст обратной связи"""
        request = DishAnalysisRequest(
            photo_url="/uploads/test.jpg",
            user_recipe_text="Test recipe",
            dish_type=DishType.DINNER
        )
        
        result = AIService.analyze_dish(request)
        
        assert result.appearance_feedback
        assert len(result.appearance_feedback) > 10
        assert result.recipe_feedback
        assert len(result.recipe_feedback) > 10
        assert result.recommendations
        assert len(result.recommendations) > 10
    
    def test_analyze_dish_contains_metadata(self):
        """Тест что анализ содержит метаданные"""
        request = DishAnalysisRequest(
            photo_url="/uploads/test.jpg",
            user_recipe_text="Test recipe",
            dish_type=DishType.DINNER
        )
        
        result = AIService.analyze_dish(request)
        
        assert result.ai_metadata is not None
        assert isinstance(result.ai_metadata, dict)
        assert "vision_model" in result.ai_metadata
        assert "llm_model" in result.ai_metadata
        assert "processing_time" in result.ai_metadata
        assert "confidence_scores" in result.ai_metadata
    
    def test_analyze_dish_different_dish_types(self):
        """Тест анализа разных типов блюд"""
        dish_types = [
            DishType.BREAKFAST,
            DishType.LUNCH,
            DishType.DINNER,
            DishType.DESSERT,
            DishType.BAKING,
            DishType.OTHER
        ]
        
        for dish_type in dish_types:
            request = DishAnalysisRequest(
                photo_url="/uploads/test.jpg",
                user_recipe_text=f"Recipe for {dish_type.value}",
                dish_type=dish_type
            )
            
            result = AIService.analyze_dish(request)
            
            assert result.dish_type_identified == dish_type.value
            assert result.ai_metadata["dish_type_identified"] == dish_type.value
    
    def test_analyze_dish_simulates_processing_time(self):
        """Тест что анализ имитирует время обработки"""
        request = DishAnalysisRequest(
            photo_url="/uploads/test.jpg",
            user_recipe_text="Test recipe",
            dish_type=DishType.DINNER
        )
        
        import time
        start_time = time.time()
        result = AIService.analyze_dish(request)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Должно пройти примерно 1 секунду (с допуском)
        assert 0.9 <= processing_time <= 2.0
        
        # Время в метаданных должно соответствовать
        assert 1.0 <= result.ai_metadata["processing_time"] <= 3.0
    
    def test_analyze_dish_confidence_scores(self):
        """Тест что оценка уверенности в допустимом диапазоне"""
        request = DishAnalysisRequest(
            photo_url="/uploads/test.jpg",
            user_recipe_text="Test recipe",
            dish_type=DishType.DINNER
        )
        
        for _ in range(10):
            result = AIService.analyze_dish(request)
            
            confidence_scores = result.ai_metadata["confidence_scores"]
            
            assert 0.6 <= confidence_scores["appearance"] <= 0.95
            assert 0.6 <= confidence_scores["recipe_match"] <= 0.9
    
    def test_analyze_dish_detected_ingredients(self):
        """Тест что анализ обнаруживает ингредиенты"""
        request = DishAnalysisRequest(
            photo_url="/uploads/test.jpg",
            user_recipe_text="Test recipe with multiple ingredients",
            dish_type=DishType.DINNER
        )
        
        result = AIService.analyze_dish(request)
        
        ingredients = result.ai_metadata["ingredients_detected"]
        
        assert isinstance(ingredients, list)
        assert len(ingredients) == 3
        assert all(isinstance(ingredient, str) for ingredient in ingredients)
    
    def test_generate_statistics_recommendations(self):
        """Тест генерации рекомендаций по статистике"""
        recommendations = AIService.generate_statistics_recommendations(
            user_id=1,
            dish_type="dinner"
        )
        
        assert isinstance(recommendations, str)
        assert len(recommendations) > 0
        
        # Рекомендации должны содержать несколько строк
        lines = recommendations.split('\n')
        assert len(lines) == 3
        
        # Каждая строка должна быть не пустой
        for line in lines:
            assert line.strip()
    
    def test_generate_statistics_recommendations_different_inputs(self):
        """Тест генерации рекомендаций с разными входными данными"""
        # Тестируем с разными типами блюд
        dish_types = ["breakfast", "lunch", "dinner", "dessert", None]
        
        for dish_type in dish_types:
            recommendations = AIService.generate_statistics_recommendations(
                user_id=1,
                dish_type=dish_type
            )
            
            assert recommendations
            assert len(recommendations.split('\n')) == 3
    
    def test_ai_service_instance(self):
        """Тест что AI сервис правильно инстанциируется"""
        from backend.services.ai_service import ai_service
        
        assert isinstance(ai_service, AIService)
        assert hasattr(ai_service, 'analyze_dish')
        assert hasattr(ai_service, 'generate_statistics_recommendations')
        
        # Проверяем что статические методы доступны через инстанс
        request = DishAnalysisRequest(
            photo_url="/uploads/test.jpg",
            user_recipe_text="Test",
            dish_type=DishType.DINNER
        )
        
        result = ai_service.analyze_dish(request)
        assert isinstance(result, AnalysisResult)

class TestAIServiceIntegration:
    """Интеграционные тесты AI сервиса"""
    
    def test_analyze_dish_with_long_recipe(self):
        """Тест анализа с длинным рецептом"""
        long_recipe = "Ингредиенты: " + ", ".join([f"ингредиент_{i}" for i in range(20)]) + ". " + \
                     "Шаги приготовления: " + " ".join([f"Шаг {i}: действие" for i in range(10)])
        
        request = DishAnalysisRequest(
            photo_url="/uploads/test.jpg",
            user_recipe_text=long_recipe,
            dish_type=DishType.DINNER
        )
        
        result = AIService.analyze_dish(request)
        
        assert result.recipe_feedback
        assert "Рецепт" in result.recipe_feedback or "ингредиент" in result.recipe_feedback.lower()
    
    def test_analyze_dish_consistency(self):
        """Тест консистентности анализа для одинаковых входных данных"""
        # В реальном AI сервисе результаты могут различаться,
        # но в нашем mock они должны быть в пределах допустимого
        request = DishAnalysisRequest(
            photo_url="/uploads/same.jpg",
            user_recipe_text="Одинаковый рецепт",
            dish_type=DishType.BREAKFAST
        )
        
        results = []
        for _ in range(5):
            results.append(AIService.analyze_dish(request))
        
        # Проверяем что все результаты валидны
        for result in results:
            assert 1 <= result.appearance_score <= 5
            assert 1 <= result.recipe_score <= 5
        
        # Оценки должны быть в разумном диапазоне относительно друг друга
        appearance_scores = [r.appearance_score for r in results]
        recipe_scores = [r.recipe_score for r in results]
        
        # Максимальная разница между оценками не должна быть слишком большой
        assert max(appearance_scores) - min(appearance_scores) <= 2
        assert max(recipe_scores) - min(recipe_scores) <= 2
    
    @pytest.mark.slow
    def test_analyze_dish_performance(self):
        """Тест производительности анализа"""
        import time
        
        request = DishAnalysisRequest(
            photo_url="/uploads/test.jpg",
            user_recipe_text="Test recipe",
            dish_type=DishType.DINNER
        )
        
        times = []
        for _ in range(5):
            start_time = time.perf_counter()
            AIService.analyze_dish(request)
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        avg_time = sum(times) / len(times)
        
        # Среднее время должно быть около 1 секунды
        assert 0.8 <= avg_time <= 1.5
        
        # Ни один запрос не должен быть слишком медленным
        assert all(t < 2.0 for t in times)
