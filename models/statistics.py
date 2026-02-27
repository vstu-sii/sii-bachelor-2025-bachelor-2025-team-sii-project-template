from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

class Statistics(Base):
    __tablename__ = 'statistics'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    dish_type = Column(String(100))
    
    # Статистика
    total_dishes = Column(Integer, default=0)
    avg_appearance_score = Column(Numeric(3, 2))
    avg_recipe_score = Column(Numeric(3, 2))
    
    # AI рекомендации
    recommendations = Column(Text)
    
    # Метаданные
    calculation_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Индексы
    __table_args__ = (
        {'unique_constraint': ('user_id', 'dish_type')},
    )
    
    def __repr__(self):
        return f"<Statistics(id={self.id}, user_id={self.user_id}, dish_type={self.dish_type})>"
