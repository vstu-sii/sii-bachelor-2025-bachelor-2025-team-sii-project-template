import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from database import SessionLocal, engine, create_tables
from models import Base, User, Dish, Rating
from schemas.user import UserCreate
from schemas.dish import DishCreate, DishType
from crud.user import create_user, get_user_by_email
from crud.dish import create_dish
from crud.rating import create_rating

def test_database_connection():
    """Тест подключения к базе данных"""
    try:
        # Создаём таблицы если их нет
        Base.metadata.create_all(bind=engine)
        
        db = SessionLocal()
        
        print("✅ Подключение к БД успешно!")
        
        # Тест создания пользователя
        user_data = UserCreate(
            username="test_user",
            email="test@example.com",
            password="testpass123"
        )
        
        user = create_user(db, user_data)
        print(f"✅ Создан пользователь: {user.username} (ID: {user.id})")
        
        # Тест создания блюда
        dish_data = DishCreate(
            dish_type=DishType.DINNER,
            user_recipe_text="Тестовый рецепт: ингредиенты и шаги приготовления... " * 10,
            photo_url="https://example.com/photo.jpg"
        )
        
        dish = create_dish(db, dish_data, user.id)
        print(f"✅ Создано блюдо: {dish.dish_type} (ID: {dish.id})")
        
        # Тест создания оценки
        from schemas.rating import RatingCreate
        rating_data = RatingCreate(
            dish_id=dish.id,
            appearance_score=4,
            recipe_score=3,
            appearance_feedback="Хороший внешний вид",
            recipe_feedback="Соответствует рецепту",
            recommendations="Можно улучшить"
        )
        
        rating = create_rating(db, rating_data)
        print(f"✅ Создана оценка: {rating.appearance_score}/{rating.recipe_score}")
        
        # Проверяем данные
        print(f"\n📊 Проверка данных:")
        print(f"Пользователей в БД: {db.query(User).count()}")
        print(f"Блюд в БД: {db.query(Dish).count()}")
        print(f"Оценок в БД: {db.query(Rating).count()}")
        
        db.close()
        print("\n🎉 Все тесты пройдены успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1)
