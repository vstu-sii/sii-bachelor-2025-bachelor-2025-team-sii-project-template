import re
import json
import datetime as dt
from random import choice, randint

def to_lower( lst ):
    for i in range(len(lst)):
        lst[i] = lst[i].lower()
    return lst

def exclude_items( a, b ):
    for item in b:
        if item in a:
            i = a.index(item)
            a = a[:i] + a[i+1:]
    return a

def get_all_products():
    with open('../data/all-products.txt', 'r') as f:
        products = [i.lower().strip() for i in f.read().split('\n') if len(i.strip()) > 0 ]
    return products

all_products = get_all_products()

def pick_goal():
    return choice(['weight_loss', 'weight_gain', 'healthy_eating','muscle_gain'])

def pick_forbidden_products( amount = -1 ):
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

def pick_available_products( amount = -1 ):
    if amount == -1:
        amount = randint( 15, 50 )
    return pick_forbidden_products( amount )

def pick_target_calories():
    return choice(['low', 'medium', 'high'])

def calories_to_word( calories ):
    if calories < 650:
        return 'low'
    elif calories < 1050:
        return 'medium'
    else:
        return 'high'

def determine_target_calories( goal ):
    # average values for goals supported.
    if goal == 'weight_loss':
        return 1500
    elif goal == 'weight_gain':
        return 3000
    elif goal == 'healthy_eating':
        return 2000
    elif goal == 'muscle_gain':
        return 2800
    return -1

def date_from_now( days_forward ):
    return (dt.datetime.now() + dt.timedelta( days = days_forward )).strftime('%Y-%m-%d')

def find_in_db( ingredient ):
    iname = ingredient.split('(')[0].lower().strip()
    # here the real database will be connected, leave json dataset for now
    with open('/home/q/Code/unik/ai/mealway/mealway-dev/data/dataset.json', 'r') as f:
        data = json.loads( f.read() )["products"]

    tmp_res = None
    for p in data:
        if iname == p['productName']:
            return p
        elif iname in p['productName']:
            tmp_res = p
    return tmp_res

def preprocess_ingredients( ingredients ):
    """
            ingredient = {
                    "productId": 0,
                    "productName": productName,
                    "quantity": 1,
                    "unit": "",
                    "cost": cost, # not like in meal cost
            }
    """
    result = []
    for i in ingredients:
        data = find_in_db( i )
        if data is None:
            continue

        imass = 0 # in gramms
        if '(' in i:
            imass = i.split('(')[1]
            imass = imass.split(' ')[0]
            try:
                imass = float(imass)
            except:
                try:
                    imass = int(imass)
                except:
                    imass = 0.0

        # calculate total mass (based on calories per 100g)
        imass = 100 * imass / data["calories"]
        result.append({
            "productId": data["productId"],
            "productName": data["productName"],
            "quantity": imass,
            "unit": "",
            "cost": data["cost"] # * round(imass / 100) # calculate price per 100g
        })
    return result

def calculate_nutrition( ingredients ):
    nutrition = {
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0,
    }
    for i in ingredients:
        data = find_in_db( i )
        if data is None:
            continue

        for key in nutrition.keys():
            nutrition[ key ] += data[ key ]
    return nutrition

def calculate_cost( ingredients ):
    total_cost = 0
    for i in ingredients:
        data = find_in_db( i )
        if data is None:
            continue
        total_cost += data["cost"] # * data.get("quantity", 1)
    return total_cost

def calculate_cost_from_shopping_list( shopping_list ):
    total_cost = 0
    for i in shopping_list:
        data = find_in_db( i["productName"] + '(' )
        if data is None:
            continue
        total_cost += data["cost"] * i.get("quantity", 1)
    return total_cost


def json2python_list(string):
    lst = []
    items = string[1:-1].split(',')
    for item in items:
        lst.append( item.replace('"', '') )
    return lst


def clean_json(string):
    print("String:", string)

    if '\n\n' in string:
        string = string.split('\n\n')[-1]
    if '}\n{\n' in string: # check if we have multiple meal plans for some reason
        string = '{\n' + string.split('}\n{')[-1]

    string = '\n'.join([ i for i in string.split('\n') if ('#' in i) == False ])
    string = string.strip().lower()

    if string.startswith("```"):
        string = '\n'.join( string.split('\n')[1:-1] )

    if string.strip().endswith('```'):
        string = '\n'.join( string.split('\n')[:-1] )

    if string.strip()[0] == '"':
        if string.strip()[1:].startswith('breakfast') == False:
            if string.strip()[1:].startswith("lunch") == False:
                if string.strip()[1:].startswith("dinner") == False:
                    string = '{\n\t"breakfast": [\n' + string
        else:
            string = '{\n\t' + string

    if string.count('"') % 2:
        string += '",'

    if string[-1] == ',':
        if string.rfind('{') > string.rfind('}'):
            string += '}'
        if '[' in string and ']' not in string:
            string += '\n]'

    # drop trailing ','
    string = re.sub(",[ \t\r\n]+}", "}", string)
    string = re.sub(",[ \t\r\n]+\]", "]", string)
    return string
