from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from enum import Enum

class DishType(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    DESSERT = "dessert"
    BAKING = "baking"
    OTHER = "other"

class DishStatus(str, Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    READY = "ready"

class DishBase(BaseModel):
    dish_type: DishType = DishType.OTHER
    user_recipe_text: str

class DishCreate(DishBase):
    photo_url: Optional[str] = None
    
    @validator('user_recipe_text')
    def validate_recipe_length(cls, v):
        if len(v) < 50:
            raise ValueError('Recipe must be at least 50 characters long')
        if len(v) > 2000:
            raise ValueError('Recipe must not exceed 2000 characters')
        return v

class DishUpdate(BaseModel):
    dish_type: Optional[DishType] = None
    user_recipe_text: Optional[str] = None
    photo_url: Optional[str] = None
    status: Optional[DishStatus] = None

class DishResponse(DishBase):
    id: int
    user_id: int
    photo_url: Optional[str]
    status: DishStatus
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class DishAnalysisRequest(BaseModel):
    photo_url: str
    user_recipe_text: str
    dish_type: DishType = DishType.OTHER
