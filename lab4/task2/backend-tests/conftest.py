import pytest
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import get_db
from backend.models import Base
from backend.api.main import create_application

# Тестовая база данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def test_db():
    """Создание тестовой базы данных"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(test_db):
    """Сессия базы данных для тестов"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    """TestClient для FastAPI"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app = create_application()
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session):
    """Тестовый пользователь"""
    from backend.crud.user import create_user
    from backend.schemas.user import UserCreate
    
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="testpassword"
    )
    
    return create_user(db_session, user_data)

@pytest.fixture
def auth_headers(client, test_user):
    """Заголовки авторизации для тестов"""
    # В реальном приложении здесь был бы JWT токен
    return {"Authorization": "Bearer mock_token"}

@pytest.fixture
def test_dish(db_session, test_user):
    """Тестовое блюдо"""
    from backend.models import Dish, DishStatus, DishType
    
    dish = Dish(
        user_id=test_user.id,
        photo_url="/uploads/test.jpg",
        dish_type=DishType.DINNER,
        user_recipe_text="Test recipe text for testing purposes" * 10,
        status=DishStatus.DRAFT
    )
    
    db_session.add(dish)
    db_session.commit()
    db_session.refresh(dish)
    
    return dish
