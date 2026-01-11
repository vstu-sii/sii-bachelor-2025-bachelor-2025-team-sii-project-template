from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import timedelta

from database import get_db
from crud.user import get_user_by_email, create_user, verify_password
from schemas.user import UserCreate, UserResponse, Token
from api.dependencies.auth import get_current_user

router = APIRouter()

# Mock функция для создания токена (в реальном приложении использовать JWT)
def create_access_token(data: dict, expires_delta: timedelta = None):
    return "mock_token_for_development"

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Регистрация нового пользователя.
    """
    # Проверяем существует ли пользователь с таким email
    db_user = get_user_by_email(db, email=user_data.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует",
        )
    
    # Создаём пользователя
    user = create_user(db, user_data)
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "created_at": user.created_at
    }

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Аутентификация пользователя и получение токена.
    """
    user = get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Создаём mock токен
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
async def read_current_user(
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Получение информации о текущем пользователе.
    """
    return current_user

@router.post("/logout")
async def logout() -> Dict[str, str]:
    """
    Выход из системы.
    """
    return {"message": "Successfully logged out"}
