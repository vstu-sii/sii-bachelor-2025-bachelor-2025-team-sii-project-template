from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os
import uuid
from datetime import datetime

from database import get_db
from crud.dish import get_dish, get_dishes, create_dish, update_dish, delete_dish, get_user_dishes_by_status
from crud.rating import create_rating, get_rating
from schemas.dish import DishCreate, DishResponse, DishUpdate, DishStatus, DishType
from schemas.rating import RatingCreate, RatingResponse
from api.dependencies.auth import get_current_active_user
from services.ai_service import ai_service

router = APIRouter()

# Папка для загрузки фото
UPLOAD_DIR = "uploads/dishes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=DishResponse, status_code=status.HTTP_201_CREATED)
async def create_new_dish(
    photo: UploadFile = File(...),
    dish_type: DishType = Form(...),
    user_recipe_text: str = Form(...),
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    Создание нового блюда с загрузкой фото.
    """
    # Сохраняем фото
    file_extension = photo.filename.split(".")[-1] if "." in photo.filename else "jpg"
    filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(photo.file, buffer)
    
    # Создаём блюдо
    dish_data = DishCreate(
        dish_type=dish_type,
        user_recipe_text=user_recipe_text,
        photo_url=f"/uploads/dishes/{filename}"
    )
    
    dish = create_dish(db, dish_data, current_user["id"])
    
    return {
        "id": dish.id,
        "user_id": dish.user_id,
        "photo_url": dish.photo_url,
        "dish_type": dish.dish_type,
        "user_recipe_text": dish.user_recipe_text,
        "status": dish.status,
        "created_at": dish.created_at,
        "updated_at": dish.updated_at
    }

@router.post("/{dish_id}/analyze", response_model=RatingResponse)
async def analyze_dish(
    dish_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    Запуск AI анализа блюда.
    """
    # Проверяем что блюдо существует и принадлежит пользователю
    dish = get_dish(db, dish_id)
    if not dish or dish.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Блюдо не найдено",
        )
    
    # Проверяем что анализ ещё не выполнялся
    existing_rating = get_rating(db, dish_id)
    if existing_rating:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Анализ для этого блюда уже выполнен",
        )
    
    # Выполняем AI анализ
    analysis_request = {
        "photo_url": dish.photo_url,
        "user_recipe_text": dish.user_recipe_text,
        "dish_type": dish.dish_type
    }
    
    analysis_result = ai_service.analyze_dish(analysis_request)
    
    # Сохраняем результат
    rating_data = RatingCreate(
        dish_id=dish_id,
        appearance_score=analysis_result.appearance_score,
        recipe_score=analysis_result.recipe_score,
        appearance_feedback=analysis_result.appearance_feedback,
        recipe_feedback=analysis_result.recipe_feedback,
        recommendations=analysis_result.recommendations,
        ai_metadata=analysis_result.ai_metadata
    )
    
    rating = create_rating(db, rating_data)
    
    return {
        "id": rating.id,
        "dish_id": rating.dish_id,
        "appearance_score": rating.appearance_score,
        "recipe_score": rating.recipe_score,
        "appearance_feedback": rating.appearance_feedback,
        "recipe_feedback": rating.recipe_feedback,
        "recommendations": rating.recommendations,
        "created_at": rating.created_at
    }

@router.get("/", response_model=List[DishResponse])
async def read_dishes(
    skip: int = 0,
    limit: int = 100,
    status: Optional[DishStatus] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[dict]:
    """
    Получение списка блюд пользователя.
    """
    if status:
        dishes = get_user_dishes_by_status(db, current_user["id"], status)
    else:
        dishes = get_dishes(db, current_user["id"], skip=skip, limit=limit)
    
    return [
        {
            "id": dish.id,
            "user_id": dish.user_id,
            "photo_url": dish.photo_url,
            "dish_type": dish.dish_type,
            "user_recipe_text": dish.user_recipe_text,
            "status": dish.status,
            "created_at": dish.created_at,
            "updated_at": dish.updated_at
        }
        for dish in dishes
    ]

@router.get("/{dish_id}", response_model=DishResponse)
async def read_dish(
    dish_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    Получение информации о конкретном блюде.
    """
    dish = get_dish(db, dish_id)
    if not dish or dish.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Блюдо не найдено",
        )
    
    return {
        "id": dish.id,
        "user_id": dish.user_id,
        "photo_url": dish.photo_url,
        "dish_type": dish.dish_type,
        "user_recipe_text": dish.user_recipe_text,
        "status": dish.status,
        "created_at": dish.created_at,
        "updated_at": dish.updated_at
    }

@router.get("/{dish_id}/analysis", response_model=RatingResponse)
async def get_dish_analysis(
    dish_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    Получение результатов анализа блюда.
    """
    dish = get_dish(db, dish_id)
    if not dish or dish.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Блюдо не найдено",
        )
    
    rating = get_rating(db, dish_id)
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Анализ для этого блюда не выполнен",
        )
    
    return {
        "id": rating.id,
        "dish_id": rating.dish_id,
        "appearance_score": rating.appearance_score,
        "recipe_score": rating.recipe_score,
        "appearance_feedback": rating.appearance_feedback,
        "recipe_feedback": rating.recipe_feedback,
        "recommendations": rating.recommendations,
        "created_at": rating.created_at
    }

@router.put("/{dish_id}", response_model=DishResponse)
async def update_dish_info(
    dish_id: int,
    dish_update: DishUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    Обновление информации о блюде.
    """
    dish = get_dish(db, dish_id)
    if not dish or dish.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Блюдо не найдено",
        )
    
    updated_dish = update_dish(db, dish_id, dish_update)
    
    return {
        "id": updated_dish.id,
        "user_id": updated_dish.user_id,
        "photo_url": updated_dish.photo_url,
        "dish_type": updated_dish.dish_type,
        "user_recipe_text": updated_dish.user_recipe_text,
        "status": updated_dish.status,
        "created_at": updated_dish.created_at,
        "updated_at": updated_dish.updated_at
    }

@router.delete("/{dish_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dish_by_id(
    dish_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> None:
    """
    Удаление блюда.
    """
    dish = get_dish(db, dish_id)
    if not dish or dish.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Блюдо не найдено",
        )
    
    success = delete_dish(db, dish_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось удалить блюдо",
        )
