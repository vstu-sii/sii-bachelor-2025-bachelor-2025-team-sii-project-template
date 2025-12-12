import os
from fastapi import FastAPI
from pydantic import BaseModel
from models.baseline import Model, DB

app = FastAPI()

def get_env_or( env_name, default_value ):
    try:
        env = os.environ[env_name]
    except:
        pass
    if not env:
        return default_value

m = Model( get_env_or("MEALWAY_MODEL", "LiquidAI/LFM2-1.2B"), None )
m.db = DB(m)

class MealPlanGenerationRequest(BaseModel):
    goal: str
    allergies: [] | None = []
    likes: [] | None = []
    dislikes: [] | None = []
    minBudget: int
    maxBudget: int
    days: int
    mealsPerDay: int

@app.post('/meal-plan/generate')
async def gen_meal_plan( req: MealPlanGenerationRequest ):
    return m.gen_meal_plan( req.goal, req.allergies, req.likes, req.dislikes, req.minBudget, req.maxBudget, req.days, req.mealsPerDay )

@app.get('/meal-plan/{planId}/shopping-list')
async def gen_shopping_list( planId ):
    plan = m.retrieve_plan_by_id(planId)
    return m.gen_shopping_list( planId, plan )
