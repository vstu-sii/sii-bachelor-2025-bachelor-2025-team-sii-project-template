from sqlalchemy import Column, Integer, String, Text, SmallInteger, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

class Rating(Base):
    __tablename__ = 'ratings'
    
    id = Column(Integer, primary_key=True, index=True)
    dish_id = Column(Integer, ForeignKey('dishes.id', ondelete='CASCADE'), unique=True, nullable=False)
    
    # Оценки от AI
    appearance_score = Column(SmallInteger)  # 1-5
    recipe_score = Column(SmallInteger)      # 1-5
    
    # Комментарии от AI
    appearance_feedback = Column(Text)
    recipe_feedback = Column(Text)
    recommendations = Column(Text)
    
    # Сырые данные от AI (если нужно сохранить)
    ai_metadata = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    dish = relationship("Dish", back_populates="rating")
    
    def __repr__(self):
        return f"<Rating(id={self.id}, dish_id={self.dish_id}, appearance={self.appearance_score}, recipe={self.recipe_score})>"
