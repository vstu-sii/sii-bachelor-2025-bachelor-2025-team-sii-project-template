from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from .base import Base

class DishType(str, enum.Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    DESSERT = "dessert"
    BAKING = "baking"
    OTHER = "other"

class DishStatus(str, enum.Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    READY = "ready"

class Dish(Base):
    __tablename__ = 'dishes'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    photo_url = Column(String(500))
    dish_type = Column(Enum(DishType), default=DishType.OTHER)
    user_recipe_text = Column(Text, nullable=False)
    status = Column(Enum(DishStatus), default=DishStatus.DRAFT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    user = relationship("User", back_populates="dishes")
    rating = relationship("Rating", back_populates="dish", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Dish(id={self.id}, dish_type={self.dish_type}, user_id={self.user_id})>"
