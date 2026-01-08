from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Получение URL базы данных из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:123@localhost/cooking_assistant")

# Создаём движок SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    echo=False  # Поставь True для дебага SQL запросов
)

# Создаём фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency для FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Функция для создания таблиц (для разработки)
def create_tables():
    from .models import Base
    Base.metadata.create_all(bind=engine)

# Функция для удаления таблиц (для тестов)
def drop_tables():
    from .models import Base
    Base.metadata.drop_all(bind=engine)
