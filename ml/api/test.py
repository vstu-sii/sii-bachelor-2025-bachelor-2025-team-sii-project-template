import json
from random import randint, choice
from locust import HttpUser, between, task

def get_all_products():
    with open('../../models/all-products.txt', 'r') as f:
        products = [i.lower().strip() for i in f.read().split('\n') if len(i.strip()) > 0 ]
    return products

all_products = get_all_products()

def pick_goal():
    return choice(['weight_loss', 'weight_gain', 'healthy_eating','muscle_gain'])

def pick_random_products( amount = -1 ):
    if amount == -1:
        amount = randint(0, 10)

    prods = []
    for i in range(amount):
        while True:
            p = choice( all_products )
            if p in prods:
                continue
            prods.append( p )
            break
    return sorted(prods)


def random_plan():
    return {
            "goal": pick_goal(),
            "allergies": pick_random_products(),
            "likes": pick_random_products(),
            "dislikes": pick_random_products(),
            "minBudget": randint(100, 1000),
            "maxBudget": randint(500, 10000),
            "days": 7,
            "mealsPerDay": choice([3, 4]),
    }

class WebsiteUser(HttpUser):
    @task
    def index(self):
        for i in range(10):
            self.client.post("/meal-plan/generate", json = json.dumps(random_plan()))

    @task
    def shoplist(self):
        for i in range(1, 11):
            self.client.get(f"/meal-plan/{i}/shopping_list")
