import pytest
from backend.crud import user, dish, rating
from backend.schemas.user import UserCreate, UserUpdate
from backend.schemas.dish import DishCreate, DishUpdate
from backend.schemas.rating import RatingCreate
from backend.models import DishStatus, DishType

class TestUserCRUD:
    def test_create_user(self, db_session):
        """Тест создания пользователя через CRUD"""
        user_data = UserCreate(
            username="newuser",
            email="new@example.com",
            password="password123"
        )
        
        created_user = user.create_user(db_session, user_data)
        
        assert created_user.id is not None
        assert created_user.username == "newuser"
        assert created_user.email == "new@example.com"
        assert created_user.is_active is True
        assert user.verify_password("password123", created_user.hashed_password)
    
    def test_get_user_by_email(self, db_session, test_user):
        """Тест получения пользователя по email"""
        found_user = user.get_user_by_email(db_session, test_user.email)
        
        assert found_user is not None
        assert found_user.id == test_user.id
        assert found_user.email == test_user.email
    
    def test_get_user_by_email_not_found(self, db_session):
        """Тест поиска несуществующего пользователя"""
        found_user = user.get_user_by_email(db_session, "nonexistent@example.com")
        assert found_user is None
    
    def test_get_user(self, db_session, test_user):
        """Тест получения пользователя по ID"""
        found_user = user.get_user(db_session, test_user.id)
        
        assert found_user is not None
        assert found_user.id == test_user.id
    
    def test_update_user(self, db_session, test_user):
        """Тест обновления пользователя"""
        update_data = UserUpdate(
            username="updateduser",
            email="updated@example.com"
        )
        
        updated_user = user.update_user(db_session, test_user.id, update_data)
        
        assert updated_user is not None
        assert updated_user.username == "updateduser"
        assert updated_user.email == "updated@example.com"
    
    def test_verify_password(self):
        """Тест проверки пароля"""
        hashed_password = user.get_password_hash("password123")
        
        assert user.verify_password("password123", hashed_password) is True
        assert user.verify_password("wrongpassword", hashed_password) is False

class TestDishCRUD:
    def test_create_dish(self, db_session, test_user):
        """Тест создания блюда через CRUD"""
        dish_data = DishCreate(
            dish_type=DishType.DINNER,
            user_recipe_text="Test recipe " * 10,
            photo_url="/uploads/test.jpg"
        )
        
        created_dish = dish.create_dish(db_session, dish_data, test_user.id)
        
        assert created_dish.id is not None
        assert created_dish.user_id == test_user.id
        assert created_dish.dish_type == DishType.DINNER
        assert created_dish.status == DishStatus.DRAFT
    
    def test_get_dish(self, db_session, test_dish):
        """Тест получения блюда по ID"""
        found_dish = dish.get_dish(db_session, test_dish.id)
        
        assert found_dish is not None
        assert found_dish.id == test_dish.id
    
    def test_get_dishes(self, db_session, test_user, test_dish):
        """Тест получения списка блюд пользователя"""
        # Создаём ещё одно блюдо
        dish_data = DishCreate(
            dish_type=DishType.BREAKFAST,
            user_recipe_text="Another recipe " * 10
        )
        dish.create_dish(db_session, dish_data, test_user.id)
        
        dishes = dish.get_dishes(db_session, test_user.id)
        
        assert len(dishes) == 2
        assert all(d.user_id == test_user.id for d in dishes)
    
    def test_get_dishes_with_limit(self, db_session, test_user):
        """Тест получения блюд с лимитом"""
        # Создаём несколько блюд
        for i in range(5):
            dish_data = DishCreate(
                dish_type=DishType.DINNER,
                user_recipe_text=f"Recipe {i} " * 10
            )
            dish.create_dish(db_session, dish_data, test_user.id)
        
        dishes = dish.get_dishes(db_session, test_user.id, skip=0, limit=3)
        
        assert len(dishes) == 3
    
    def test_update_dish(self, db_session, test_dish):
        """Тест обновления блюда"""
        update_data = DishUpdate(
            dish_type=DishType.LUNCH,
            user_recipe_text="Updated recipe text"
        )
        
        updated_dish = dish.update_dish(db_session, test_dish.id, update_data)
        
        assert updated_dish is not None
        assert updated_dish.dish_type == DishType.LUNCH
        assert updated_dish.user_recipe_text == "Updated recipe text"
    
    def test_delete_dish(self, db_session, test_dish):
        """Тест удаления блюда"""
        result = dish.delete_dish(db_session, test_dish.id)
        
        assert result is True
        
        # Проверяем что блюдо удалено
        deleted_dish = dish.get_dish(db_session, test_dish.id)
        assert deleted_dish is None
    
    def test_delete_nonexistent_dish(self, db_session):
        """Тест удаления несуществующего блюда"""
        result = dish.delete_dish(db_session, 99999)
        assert result is False
    
    def test_get_user_dishes_by_status(self, db_session, test_user):
        """Тест получения блюд по статусу"""
        # Создаём блюда с разными статусами
        dish_data1 = DishCreate(
            dish_type=DishType.DINNER,
            user_recipe_text="Recipe 1"
        )
        dish1 = dish.create_dish(db_session, dish_data1, test_user.id)
        
        dish_data2 = DishCreate(
            dish_type=DishType.BREAKFAST,
            user_recipe_text="Recipe 2"
        )
        dish2 = dish.create_dish(db_session, dish_data2, test_user.id)
        
        # Обновляем статус второго блюда
        dish2.status = DishStatus.READY
        db_session.commit()
        
        # Получаем блюда по статусу
        draft_dishes = dish.get_user_dishes_by_status(db_session, test_user.id, DishStatus.DRAFT)
        ready_dishes = dish.get_user_dishes_by_status(db_session, test_user.id, DishStatus.READY)
        
        assert len(draft_dishes) == 1
        assert len(ready_dishes) == 1
        assert draft_dishes[0].id == dish1.id
        assert ready_dishes[0].id == dish2.id

class TestRatingCRUD:
    def test_create_rating(self, db_session, test_dish):
        """Тест создания оценки через CRUD"""
        rating_data = RatingCreate(
            dish_id=test_dish.id,
            appearance_score=4,
            recipe_score=3,
            appearance_feedback="Good appearance",
            recipe_feedback="Good recipe",
            recommendations="Improve presentation",
            ai_metadata={"model": "gpt-4"}
        )
        
        created_rating = rating.create_rating(db_session, rating_data)
        
        assert created_rating.id is not None
        assert created_rating.dish_id == test_dish.id
        assert created_rating.appearance_score == 4
        assert created_rating.ai_metadata == {"model": "gpt-4"}
    
    def test_get_rating(self, db_session, test_dish):
        """Тест получения оценки"""
        # Сначала создаём оценку
        rating_data = RatingCreate(
            dish_id=test_dish.id,
            appearance_score=4,
            recipe_score=3,
            appearance_feedback="Test",
            recipe_feedback="Test",
            recommendations="Test"
        )
        created_rating = rating.create_rating(db_session, rating_data)
        
        # Затем получаем её
        found_rating = rating.get_rating(db_session, test_dish.id)
        
        assert found_rating is not None
        assert found_rating.id == created_rating.id
    
    def test_update_rating(self, db_session, test_dish):
        """Тест обновления оценки"""
        # Сначала создаём оценку
        rating_data = RatingCreate(
            dish_id=test_dish.id,
            appearance_score=4,
            recipe_score=3,
            appearance_feedback="Original",
            recipe_feedback="Original",
            recommendations="Original"
        )
        created_rating = rating.create_rating(db_session, rating_data)
        
        # Обновляем оценку
        update_data = {
            "appearance_score": 5,
            "recipe_score": 4,
            "appearance_feedback": "Updated"
        }
        
        updated_rating = rating.update_rating(db_session, test_dish.id, update_data)
        
        assert updated_rating is not None
        assert updated_rating.appearance_score == 5
        assert updated_rating.appearance_feedback == "Updated"
