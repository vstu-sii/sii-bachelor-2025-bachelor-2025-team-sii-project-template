from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from sqlalchemy.orm import Session

from database import get_db
from crud.user import get_user_by_email

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[dict]:
    """
    Mock аутентификация пользователя.
    В реальном приложении здесь была бы проверка JWT токена.
    """
    # Для разработки возвращаем тестового пользователя
    # В реальном приложении декодировали бы JWT токен
    user = get_user_by_email(db, email="test@example.com")
    if not user:
        # Если тестового пользователя нет, создаём его
        from crud.user import create_user
        from schemas.user import UserCreate
        user_data = UserCreate(
            username="test_user",
            email="test@example.com",
            password="testpass123"
        )
        user = create_user(db, user_data)
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "created_at": user.created_at
    }

async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Проверяет что пользователь активен"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неавторизованный доступ",
        )
    return current_user
