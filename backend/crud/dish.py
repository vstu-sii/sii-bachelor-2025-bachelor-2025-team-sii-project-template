from sqlalchemy.orm import Session
from typing import List, Optional
from ..models import Dish, DishStatus
from ..schemas.dish import DishCreate, DishUpdate

def get_dish(db: Session, dish_id: int) -> Optional[Dish]:
    return db.query(Dish).filter(Dish.id == dish_id).first()

def get_dishes(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Dish]:
    return db.query(Dish).filter(Dish.user_id == user_id).offset(skip).limit(limit).all()

def create_dish(db: Session, dish: DishCreate, user_id: int) -> Dish:
    db_dish = Dish(
        **dish.dict(),
        user_id=user_id,
        status=DishStatus.DRAFT
    )
    db.add(db_dish)
    db.commit()
    db.refresh(db_dish)
    return db_dish

def update_dish(db: Session, dish_id: int, dish_update: DishUpdate) -> Optional[Dish]:
    db_dish = get_dish(db, dish_id)
    if db_dish:
        update_data = dish_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_dish, field, value)
        db.commit()
        db.refresh(db_dish)
    return db_dish

def delete_dish(db: Session, dish_id: int) -> bool:
    db_dish = get_dish(db, dish_id)
    if db_dish:
        db.delete(db_dish)
        db.commit()
        return True
    return False

def get_user_dishes_by_status(db: Session, user_id: int, status: DishStatus) -> List[Dish]:
    return db.query(Dish).filter(
        Dish.user_id == user_id,
        Dish.status == status
    ).all()
