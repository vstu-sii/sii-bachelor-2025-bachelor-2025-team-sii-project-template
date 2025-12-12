RECEIPT_GEN_PROMPT = '''
Generate a receipt for {meal}. Ensure the total dish calorie content is approximately {target_calories} kcal. Calculate and include the calories for each ingredient during receipt creation. For example (do not respond with this example):
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

GEN_MEAL_PROMPT = """
My goal is {goal}. Please generate a meal plan consisting of {meals_amount} meals. I like to eat {likes} and dislike {dislikes}; exclude these from the plan."""

GEN_MEAL_WITH_ALERGIES_PROMPT = """
I am allergic to {allergies}. Do not include any of these in my meal plan."""

GEN_MEAL_RESPONSE_PROMPT = """
Please list the meal names in order: breakfast, lunch, dinner, and snacks. Example:

coffee with a sandwich
chicken soup
pasta with fried chicken
"""
