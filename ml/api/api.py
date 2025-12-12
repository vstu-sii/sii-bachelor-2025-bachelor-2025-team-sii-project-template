import os
from fastapi import FastAPI, Request, HTTPException
from fastapi_throttling import ThrottlingMiddleware
"""from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
"""
from pydantic import BaseModel
from models.baseline import Model, DB

# rate limit by ip
#limiter = Limiter( key_func = get_remote_address )
app = FastAPI()
#app.state.limiter = limiter
#app.add_exception_handler( RateLimitExceeded, _rate_limit_exceeded_handler )
app.add_middleware(ThrottlingMiddleware, limit=100, window=60)

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
#@limiter.limit("10/minute")
async def gen_meal_plan( req: MealPlanGenerationRequest ):
    return m.gen_meal_plan( req.goal, req.allergies, req.likes, req.dislikes, req.minBudget, req.maxBudget, req.days, req.mealsPerDay )

@app.get('/meal-plan/{planId}/shopping-list')
#@limiter.limit("10/minute")
async def gen_shopping_list( planId ):
    plan = m.retrieve_plan_by_id(planId)
    return m.gen_shopping_list( planId, plan )
