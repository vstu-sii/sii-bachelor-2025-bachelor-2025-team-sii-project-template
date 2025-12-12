import os
import re
import json
from dotenv import load_dotenv
from langfuse import observe, get_client
from langchain.llms import HuggingFacePipeline
from transformers import pipeline
from langchain.chains import LLMChain
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

from langgraph.cache.memory import InMemoryCache
from langchain_core.globals import set_llm_cache

from prompt_templates import *
from util import *

"""
Must be called before creating a model.
The only thing this function does is setting up
models cache directory.
"""
def init_module():
    load_dotenv()
    if os.path.exists("./models") == False:
        os.mkdir('./models')
    os.environ["TRANSFORMERS_CACHE"] = os.getenv("MODEL_CACHE_DIR", "./models")



def new_model( model_name, max_length=65536, temperature=0.7 ):
    """
    Initialize a local transformer model for LangChain integration
    In:
        model_name - HuggingFace model identifier
    Out:
        llm - LangChain-compatible LLM instance
    """
    cache = InMemoryCache()
    #set_llm_cache( cache )
    text_generator = pipeline( "text-generation",
                              model = model_name,
                              max_length = max_length,
                              temperature = temperature,
                              cache = cache )
    llm = HuggingFacePipeline( pipeline = text_generator )
    return llm


"""
Model for meal planner.
Constructor parameters are just basic parameters every model needs,
set with some sane values by default.

Model has 3 chats: meal planner, shopping list creator, receipt generator.
You should use the relevant function yourself.
"""
class Model:
    def __init__(self,
                 model_name,
                 max_length= 1000, # 65536,
                 temperature=0.7,
                 verbose=True,
                 max_retries=5):

        # load model
        self.model = new_model( model_name, max_length, temperature )
        # initialize prompts for different tasks.
        self.receipt_gen_prompt = PromptTemplate(
                input_variables = ["meal", "forbidden_products"],
                template = RECEIPT_GEN_PROMPT
        )
        self.meal_plan_prompt = PromptTemplate(
            input_variables = ["forbidden_products", "available_products", "target_calories", "meal"],
            template = MEAL_PROMPT #MEAL_PLAN_PROMPT
        )
        self.eatable_prompt = PromptTemplate(
            input_variables = ["dish"],
            template = """Can the dish named "{dish}" be eaten with joy? Response only with 'yes' or 'no'."""
        )

        # initialize chats
        self.receipt_gen_chat = LLMChain(
                llm = self.model,
                prompt = self.receipt_gen_prompt,
                verbose = verbose
        )
        self.meal_plan_chat = LLMChain(
                llm = self.model,
                prompt = self.meal_plan_prompt,
                verbose = verbose
        )
        self.eatable_chat = LLMChain(
                llm = self.model,
                prompt = self.eatable_prompt,
                verbose = verbose
        )
        self.verbose = verbose
        self.max_retries = max_retries

    def retrieve_plan_by_id(self, planId):
        # must be discussed with devops and fullstack
        pass

    def metrics(self, amount=1):

        failed_shopping_list = 0
        failed_receipt = 0
        failed_meal_plan = 0
        success_shopping_list = 0
        success_receipt = 0
        success_meal_plan = 0

        for i in range(amount):
            # use written functions
            allergies = pick_forbidden_products()
            dislikes = pick_forbidden_products()
            likes = pick_available_products()
            goal = pick_goal()
            minBudget = 1000
            maxBudget = 5000
            days=1
            mealsPerDay = 1

            response = self.gen_meal_plan( goal, allergies, likes, dislikes, minBudget, maxBudget, days, mealsPerDay )
            meals = response["plan"]["days"]
            shoppingList = response["plan"]["shoppingList"]

            totalCalories = 0
            # check meal plan
            for dayPlan in meals:
                dayMeals = dayPlan["meals"]
                for m in dayMeals:
                    totalCalories += m["calories"]
                    ingredients = m["ingredients"]
                    mealPlanCost = sum([x["cost"] for x in ingredients])
                    if any(map(lambda x: x["productName"] in allergies, ingredients)):
                        print("[-] Allergic product included in meal plan")
                        failed_meal_plan += 1
                    elif mealPlanCost > maxBudget:
                        print("[-] Too expensive meal plan:")
                    else:
                        success_meal_plan += 1
            print("Goal:", goal, ", calories per day:", totalCalories / 7)

            if any( map(lambda item: item["productName"] in allergies, shoppingList) ):
                print("[-] Allergic product included in shopping list.")
                failed_shopping_list+=1
            else:
                success_shopping_list+=1


        # some statistics here.
        failed_total = failed_shopping_list + failed_receipt + failed_meal_plan
        success_total = success_shopping_list + success_receipt + success_meal_plan
        total_tests = failed_total + success_total
        success_percentage = 100 * (success_total / total_tests)

        print("----- Tests are finished -----")
        print(f"- Results: {failed_total} of {total_tests} are failed")
        print(f"           {success_total}/{total_tests} are ok ({success_percentage}%)")
        print("------------------------------")

    def preprocess_dish(self, dish_name, forbidden_products):
        dish_name = dish_name.lower().strip()
        for product in forbidden_products:
            if product in dish_name:
                dish_name = dish_name.replace( product, '' )
        return dish_name

    def is_dish_eatable(self, dish):
        if '/' in dish:
            return False
        if ':' in dish:
            return False

        response = self.eatable_chat.run(
                dish = dish
        )
        response = response.replace("'", '').replace('"', '').strip()
        print("[is_dish_eatable]:", response)
        if 'yes' in response.lower():
            return True
        else:
            return False

    def gen_meal_plan(self, goal, allergies, likes, dislikes, minBudget, maxBudget, days=7, mealsPerDay=4):

        if minBudget <= 0 or maxBudget <= 0 or minBudget > maxBudget:
            return {"error": "INVALID_BUDGET", "message": "Budget range is invalid (minBudget must be <= maxBudget)"}
        if days <= 0:
            return {"error": "INVALID_DAYS", "message": "Invalid amount of days"}
        if mealsPerDay <= 0:
            return {"error": "INVALID_MEALS_PER_DAY", "message": "Invalid amount of meals per day(<=0)"}
        if target_calories <= 0:
            return {"error": "INVALID_CALORIES", "message": "Target calories must be positive"}

        allergies = to_lower( allergies )
        likes = to_lower( likes )
        dislikes = to_lower( dislikes )

        likes = exclude_items( likes, allergies )
        likes = exclude_items( likes, dislikes )

        # minimal and maximal budget per day.
        mn = minBudget / days
        mx = maxBudget / days

        daysPlans = []
        weeklyNutrition = []
        wnut = {
                "calories": 0,
                "protein": 0,
                "carbs": 0,
                "fat": 0,
        }

        for day in range(days):
            #for meal in range(mealsPerDay):
            meal = self.gen_day_plan( day+1, goal, allergies, likes, dislikes, mn, mx, mealsPerDay )
            weeklyNutrition.append( meal["dailyNutrition"] )

            for key in ["calories", "protein", "carbs", "fat"]:
                wnut[ key ] += meal["dailyNutrition"][ key ]

            daysPlans.append( meal )

        shopping_list = self.build_shopping_list( daysPlans )

        totalCalories = wnut["calories"]
        averageDailyCalories = totalCalories / days
        proteinPercentage = 100 * (wnut["protein"] / wnut["calories"])
        carbsPercentage = 100 * (wnut["carbs"] / wnut["calories"])
        fatPercentage = 100 * (wnut["carbs"] / wnut["calories"])

        plan = {
                "days": daysPlans,
                "shoppingList": shopping_list,
                "totalCost": calculate_cost_from_shopping_list( shopping_list ),
                "weeklyNutrition": weeklyNutrition,
        }
        response = {
                "success": True,
                "plan": plan,
                "totalCost": plan["totalCost"],
                "caloriesPerDay": averageDailyCalories,
                "nutritionSummary": {
                    "totalCalories": totalCalories,
                    "averageDailyCalories": averageDailyCalories,
                    "proteinPercentage": proteinPercentage,
                    "carbsPercentage": carbsPercentage,
                    "fatPercentage": fatPercentage,
                }
        }
        return response

    @observe
    def _gen_meals(self, goal, allergies, likes, dislikes, mealsAmount):

        final_response = []
        prompt_text = GEN_MEAL_PROMPT + (GEN_MEAL_WITH_ALERGIES_PROMPT + GEN_MEAL_RESPONSE_PROMPT if allergies else GEN_MEAL_RESPONSE_PROMPT)
        prompt = PromptTemplate(
                input_variables=["goal", "allergies", "likes", "dislikes", "meals_amount"],
                template = prompt_text
        )

        attempt = 0
        while (len(final_response) < mealsAmount) and (attempt < self.max_retries):
            new_chat = LLMChain(
                    llm = self.model,
                    prompt = prompt,
                    verbose = self.verbose
            )
            response = new_chat.run(
                    goal = goal,
                    allergies = ', '.join( allergies ),
                    likes = ', '.join( likes ),
                    dislikes = ', '.join( dislikes ),
                    meals_amount = mealsAmount,
            ).lower()

            while '\n\n' in response:
                response = response.strip().replace('\n\n', '\n')

            lines = [line for line in response.split('\n') if len(line) < 120 and len(line.strip()) > 3 and line.strip()[-1] != ':' and line.strip()[0] != '-']
            # lines = [line for line in lines if all(map(lambda x: x in line == False, ['please', 'confirm', 'validate']))]
            print("[*] _gen_meals(): AI response:")
            print( lines )
            final_response += lines
            attempt += 1

        return final_response

    def gen_day_plan( self, dayNumber, goal, allergies, likes, dislikes, mn, mx, mealsPerDay ):

        meals = []
        dailyCost = 0
        cost = 0
        calories = 0
        protein = 0
        carbs = 0
        fat = 0

        targetCalories = determine_target_calories( goal )
        if targetCalories < 0:
            raise ValueError("invalid goal")

        meals_names = self._gen_meals( goal, allergies, likes, dislikes, mealsPerDay ) 
        for i in range( mealsPerDay ):

            typ = "breakfast"
            if i == 1:
                typ = "lunch"
            elif i == 2:
                typ = "dinner"
            elif i > 2:
                typ = "snack"

            name = meals_names[i].lower()
            print("name =", name)
            if ':' in name:
                parts = name.split(':')
                if len(parts) == 2:
                    name = parts[1].strip()
                    typ = parts[0].strip()
                    if ' ' in typ:
                        typ = 'snack'

            print("[DEBUG] name -", name, ", typ -", typ, meals_names[i])

            receipt_out = self.gen_receipt( name, allergies, targetCalories / mealsPerDay )
            attempt = 0
            while not( receipt_out.get('receipt') ) or receipt_out["meal"].strip().lower() in name or name in receipt_out["meal"].strip().lower():
                receipt_out = self.gen_receipt( name, allergies, targetCalories / mealsPerDay )
                attempt += 1
                if attempt >= self.max_retries:
                    raise TimeoutError("failed to generate receipt for meal " + name)
            
            ingredients = preprocess_ingredients( receipt_out["ingredients"] )
            nutrition = calculate_nutrition( receipt_out["ingredients"] )
            cost = calculate_cost( receipt_out["ingredients"] )
            dailyCost += cost

            preparationTime = 'this-is-an-unsupported-yet'

            calories += nutrition["calories"]
            protein += nutrition["protein"]
            carbs += nutrition["carbs"]
            fat += nutrition["fat"]
            
            meal = {
                    "type": typ, # breakfast, lunch, dinner, snack
                    "name": name,
                    "description": "",
                    "ingredients": ingredients,
                    "instructions": receipt_out["receipt"],
                    "preparationTime": preparationTime,
                    "calories": receipt_out["calories"],
                    "nutrition": nutrition,
                    "cost": cost,
            }
            meals.append( meal )

        dailyNutrition = {
                "calories": calories,
                "protein": protein,
                "carbs": carbs,
                "fat": fat,
        }

        day_plan = {
            "dayNumber": dayNumber,
            "date": date_from_now( dayNumber ),
            "meals": meals,
            "dailyCost": dailyCost,
            "dailyNutrition": dailyNutrition,
        }
        return day_plan



    """
    Generates a shopping list based on meals.
    In:
        meals - a list of meals user would like to cook.
        forbidden_products - allergies and etc. (just in case something goes wrong)
    Out:
        shopping_list - pythonic list of products to buy.
    """
    def gen_shopping_list(self, planId, plan):
        return {
                "planId": planId,
                "totalEstimatedCost": plan["totalCost"],
                "items": plan["shoppingList"],
                "optimizationTips": []
        }

    """
    builds a shopping list according to daily plans content.
    """
    def build_shopping_list( self, daysPlans ):
        total_ingredients = []

        for day_plan in daysPlans:
            for meal in day_plan["meals"]:
                total_ingredients += meal["ingredients"]
        
        i = 0
        while i < len(total_ingredients):
            for j in range(i+1, len(total_ingredients)):
                if total_ingredients[i]["productId"] == total_ingredients[j]["productId"]:
                    total_ingredients[i]["quantity"] += total_ingredients[j]["quantity"]
                    total_ingredients = total_ingredients[i:j] + total_ingredients[j+1:]
                    i -= 1
                    break
            i += 1
        return total_ingredients

    """
    backuped function.
    """
    def gen_shopping_list_ex(self, planId, ingredients, already_have):
        lst = []
        items = []
        daysNeeded = 0
        for i in ingredients:
            parts = i.split('(')
            if parts[0].lower() in already_have:
                pass
            lst.append( parts[0].lower() )
            item = {
                    "productId": productId,
                    "productName": productName,
                    "totalQuantity": totalQuantity, # double
                    "unit": "",
                    "totalCost": totalCost, # double
                    "daysNeeded": daysNeeded # wtf?
            }
        #return lst
        response = {
                "planId": planId,
                "totalEstimatedCost": totalEstimatedCost,
                "items": items,
                "optimizationTips": [],
        }
        return response

    def filter_shoplist_item( self, i ):
        i = i.lower()
        cookwords = ['grilled', 'roasted', 'steamed', 'whole', 'mixed']
        for word in cookwords:
            if word + ' ' in i:
                i = i.replace(word + ' ', '')
        return i.strip()

    """
    Generates a receipt for a meal.
    In:
        meal - the name of meal to generate receipt for
        forbidden_products - allergies and etc. (because meal can contains some of these by default)
    Out:
        receipt - a map of "meal_name", "ingredients" and "receipt" - description of the way to cook a dish.
    """
    @observe
    def gen_receipt(self, meal, forbidden_products, target_calories):
        
        response = ''
        while len(response) < 10:
            response = self.receipt_gen_chat.run(
                    meal = meal,
                    forbidden_products = forbidden_products,
                    target_calories = target_calories,
            )

            if '```' in response:
                parts = response.split('```')
                for part in parts:
                    part = part.strip()
                    if part.startswith('json\n'):
                        part = part[5:]
                    if len(part) < 2:
                        continue

                    if part[0] == '{' and part[-1] == '}':
                        response = part
                        break

            try:
                response = clean_json( response )
                print("(gen_receipt) Response:", response)
                response = json.loads( response )
                try:
                    if type(response["ingredients"]) == dict:
                        tmp = []
                        for k, v in response["ingredients"].items():
                            tmp.append( k + '(' + str(v) + ' cal)')
                        response["ingredients"] = tmp
                    else:
                        tmp = []
                        for item in response["ingredients"]:
                            if type(item) == dict:
                                tmp.append( item["name"] + " (" + str(item["calories"]) + ")" )
                            else:
                                tmp.append( item )
                        response["ingredients"] = tmp

                    if response.get('instructions'):
                        response['receipt'] = '\n'.join( response.get('instructions') )

                    response["calories"] = target_calories
                    return response
                except Exception as e:
                    print(e)
                    pass
            except Exception as e:
                print("[-] Failed to parse receipt:", e)
                response = ''
