RECEIPT_GEN_PROMPT = '''
Generate receipt for {meal}.
Please, make the dish {target_calories} calorial.
Calculate calories during receipt generation. Example of receipt generated (just example, don't response with that):
```
{{
    "meal": "Nuts coctail",
    "ingredients": [
        "milk (200 cal)",
        "nuts (700 cal)",
    ],
    "receipt": "Cut the nuts and put them in milk.\\nYour coctail is ready!"
}}
```
'''


SHOPPING_LIST_PROMPT = """
Here are the meals user wants to cook: {meals}.
Create a shopping list for user, response in JSON format: ["product1", "product2", ...]
Do NOT include the following products in the list: {forbidden_products}.
Response with JSON list of items to buy: ["<item_1>", "<item_2", ..., etc.]. Do not generate any other output.
"""

MEAL_PLAN_PROMPT = """
User wants to eat {target_calories} calorial food.
Here are the products they would like to include in their meals: {available_products}. Here are the products you MUST NOT include even if user wants to: {forbidden_products},
Create a detailed meal plan for a day, including breakfast, lunch, and dinner. Present the output strictly in the following valid JSON format, using lists for each meal type:

{{
  "breakfast": ["<meal_1> (<meal_1_calories_count>)", "<meal_2> (<meal_2_calories_count>)", ...],
  "lunch": ["<meal_3> (<meal_3_calories_count>)"],
  "dinner": ["<meal_4> (<meal_4_calories_count>)"]
}}

Ensure that each list contains one or more meal items, describing typical dishes or ingredients for the meal. Each meal item should be a string. Do not include any explanations outside the JSON structure. Do NOT use emojis.
"""


MEAL_PROMPT = """
User wants to eat {target_calories} calorial food.
Here are the products they would like to include in their meals: {available_products}. Here are the products you MUST NOT include even if user wants to: {forbidden_products}.
What would you recommend the user to eat for {meal}? Combine some ingredients, you can add some more of them, just be careful and do NOT include ingredients from forbidden products list. Do NOT use more than 5 of ingredients.
Response with only one line which contains the name of the dish. Do NOT use lists, tuples, sets or JSON format for response.
"""

GEN_MEAL_PROMPT = """
My goal is {goal}. Please, generate a meal plan for me.
I like eat {likes}. I also dislike {dislikes}, please do NOT include them in my meal plan of {meals_amount} meals."""

GEN_MEAL_WITH_ALERGIES_PROMPT = """
I am also allergic at {allergies}. Do NOT include any of it in my meal plan."""

GEN_MEAL_RESPONSE_PROMPT = """
Response with a list of meals names, according to the order of the meals( breakfast, lunch, dinner, maybe some snacks ).
Example of response:

cofee with a sandwitch
chicken soup
pasta with fried chicken

"""
