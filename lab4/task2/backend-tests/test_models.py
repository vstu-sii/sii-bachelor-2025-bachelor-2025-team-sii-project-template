import pytest
from datetime import datetime
from backend.models import User, Dish, Rating, DishType, DishStatus

class TestUserModel:
    def test_create_user(self, db_session):
        """Тест создания пользователя"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password"
        )
        
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.is_verified is False
        assert user.created_at is not None
    
    def test_user_repr(self):
        """Тест строкового представления пользователя"""
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password"
        )
        
        assert repr(user) == "<User(id=1, username=testuser, email=test@example.com)>"
    
    def test_user_relationships(self, db_session, test_user, test_dish):
        """Тест отношений пользователя"""
        assert len(test_user.dishes) == 1
        assert test_user.dishes[0].id == test_dish.id

class TestDishModel:
    def test_create_dish(self, db_session, test_user):
        """Тест создания блюда"""
        dish = Dish(
            user_id=test_user.id,
            photo_url="/uploads/test.jpg",
            dish_type=DishType.DINNER,
            user_recipe_text="Test recipe " * 5,
            status=DishStatus.DRAFT
        )
        
        db_session.add(dish)
        db_session.commit()
        
        assert dish.id is not None
        assert dish.user_id == test_user.id
        assert dish.dish_type == DishType.DINNER
        assert dish.status == DishStatus.DRAFT
        assert dish.created_at is not None
    
    def test_dish_repr(self):
        """Тест строкового представления блюда"""
        dish = Dish(
            id=1,
            user_id=1,
            dish_type=DishType.DINNER
        )
        
        assert repr(dish) == "<Dish(id=1, dish_type=DishType.DINNER, user_id=1)>"
    
    def test_dish_enum_values(self):
        """Тест значений перечислений"""
        assert DishType.BREAKFAST.value == "breakfast"
        assert DishType.LUNCH.value == "lunch"
        assert DishType.DINNER.value == "dinner"
        assert DishType.DESSERT.value == "dessert"
        assert DishType.BAKING.value == "baking"
        assert DishType.OTHER.value == "other"
        
        assert DishStatus.DRAFT.value == "draft"
        assert DishStatus.PROCESSING.value == "processing"
        assert DishStatus.READY.value == "ready"
    
    def test_dish_rating_relationship(self, db_session, test_dish):
        """Тест отношения блюда и оценки"""
        rating = Rating(
            dish_id=test_dish.id,
            appearance_score=4,
            recipe_score=3,
            appearance_feedback="Good",
            recipe_feedback="OK",
            recommendations="Improve"
        )
        
        db_session.add(rating)
        db_session.commit()
        
        assert test_dish.rating is not None
        assert test_dish.rating.id == rating.id
        assert test_dish.rating.appearance_score == 4

class TestRatingModel:
    def test_create_rating(self, db_session, test_dish):
        """Тест создания оценки"""
        rating = Rating(
            dish_id=test_dish.id,
            appearance_score=4,
            recipe_score=3,
            appearance_feedback="Блюдо выглядит аппетитно",
            recipe_feedback="Рецепт выполнен правильно",
            recommendations="Можно улучшить подачу",
            ai_metadata={"confidence": 0.85}
        )
        
        db_session.add(rating)
        db_session.commit()
        
        assert rating.id is not None
        assert rating.dish_id == test_dish.id
        assert rating.appearance_score == 4
        assert rating.recipe_score == 3
        assert rating.appearance_feedback == "Блюдо выглядит аппетитно"
        assert rating.ai_metadata == {"confidence": 0.85}
        assert rating.created_at is not None
    
    def test_rating_repr(self):
        """Тест строкового представления оценки"""
        rating = Rating(
            id=1,
            dish_id=1,
            appearance_score=4,
            recipe_score=3
        )
        
        assert repr(rating) == "<Rating(id=1, dish_id=1, appearance=4, recipe=3)>"
    
    def test_rating_score_range(self, db_session, test_dish):
        """Тест допустимого диапазона оценок"""
        # Должны приниматься оценки от 1 до 5
        rating = Rating(
            dish_id=test_dish.id,
            appearance_score=5,  # Максимальная оценка
            recipe_score=1,      # Минимальная оценка
            appearance_feedback="Test",
            recipe_feedback="Test",
            recommendations="Test"
        )
        
        db_session.add(rating)
        db_session.commit()
        
        assert rating.appearance_score == 5
        assert rating.recipe_score == 1
    
    def test_rating_unique_constraint(self, db_session, test_dish):
        """Тест уникальности оценки для блюда"""
        rating1 = Rating(
            dish_id=test_dish.id,
            appearance_score=4,
            recipe_score=3,
            appearance_feedback="Test",
            recipe_feedback="Test",
            recommendations="Test"
        )
        
        db_session.add(rating1)
        db_session.commit()
        
        # Попытка создать вторую оценку для того же блюда должна вызвать ошибку
        rating2 = Rating(
            dish_id=test_dish.id,
            appearance_score=5,
            recipe_score=4,
            appearance_feedback="Test 2",
            recipe_feedback="Test 2",
            recommendations="Test 2"
        )
        
        db_session.add(rating2)
        
        # SQLAlchemy проверяет уникальность при коммите
        import sqlalchemy.exc
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            db_session.commit()
