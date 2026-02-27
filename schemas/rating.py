from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RatingBase(BaseModel):
    appearance_score: int
    recipe_score: int
    appearance_feedback: str
    recipe_feedback: str
    recommendations: str

class RatingCreate(RatingBase):
    dish_id: int
    ai_metadata: Optional[dict] = None

class RatingResponse(RatingBase):
    id: int
    dish_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class AnalysisResult(BaseModel):
    """Результат анализа от AI"""
    appearance_score: int
    recipe_score: int
    appearance_feedback: str
    recipe_feedback: str
    recommendations: str
    ai_metadata: Optional[dict] = None
