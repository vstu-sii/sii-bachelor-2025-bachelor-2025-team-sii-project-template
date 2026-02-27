from sqlalchemy.orm import Session
from typing import Optional
from ..models import Rating, Dish, DishStatus
from ..schemas.rating import RatingCreate

def get_rating(db: Session, dish_id: int) -> Optional[Rating]:
    return db.query(Rating).filter(Rating.dish_id == dish_id).first()

def create_rating(db: Session, rating: RatingCreate) -> Rating:
    db_rating = Rating(**rating.dict())
    db.add(db_rating)
    
    # Обновляем статус блюда
    dish = db.query(Dish).filter(Dish.id == rating.dish_id).first()
    if dish:
        dish.status = DishStatus.READY
    
    db.commit()
    db.refresh(db_rating)
    return db_rating

def update_rating(db: Session, dish_id: int, rating_update: dict) -> Optional[Rating]:
    db_rating = get_rating(db, dish_id)
    if db_rating:
        for field, value in rating_update.items():
            setattr(db_rating, field, value)
        db.commit()
        db.refresh(db_rating)
    return db_rating
