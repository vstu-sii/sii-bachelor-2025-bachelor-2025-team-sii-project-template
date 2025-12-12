RECEIPT_GEN_PROMPT = """
Generate receipt for {meal}.
Do NOT include the following products: {forbidden_products}.
"""
SHOPPING_LIST_PROMPT = """
Here are the meals user wants to cook: {meals}.
Create a shopping list for user, response in JSON format: ["product1", "product2", ...]
Do NOT include the following products in the list: {forbidden_products}.
Response with JSON-like list of items to buy: ["<item_1>", "<item_2", ..., etc.]
"""
MEAL_PLAN_PROMPT = """
User wants to eat {target_calories} calorial food.
Here are the products they would like to include in their meals: {available_products}. Here are the products you MUST NOT include even if user wants to: {forbidden_products},
Create a detailed meal plan for a day, including breakfast, lunch, and dinner. Present the output strictly in the following valid JSON format, using lists for each meal type:

{{
  "breakfast": ["<meal_1>", "<meal_2>", ...],
  "lunch": ["<meal_3>"],
  "dinner": ["<meal_4>"]
}}

Ensure that each list contains one or more meal items, describing typical dishes or ingredients for the meal. Each meal item should be a string. Do not include any explanations outside the JSON structure.
"""
