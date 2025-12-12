import os
import json
import evaluate
from baseline import *


def gen_receipts( names, calories ):
    m = Model()
    res = []
    for i in range(len(names)):
        out = m.gen_receipt( names[i], [], calories[i] )
        res.append( out.get("receipt", "") )
    return res

def original_receipts( amount=10 ):

    folder = "../data/receipts"
    files = os.listdir( folder )[:amount]
    receipts = []
    names = []
    calories = []

    for f in files:
        with open(f) as file:
            data = file.read()
            try:
                obj = json.loads( data )
                typ = obj["typ"]
                name = obj["name"]
                cal = obj["calories"]
                receipt = obj["instructions"]

                names.append( name )
                calories.append( cal )
                receipts.append( receipt )
            except Exception as e:
                print("[-] Invalid receipt in", f)
    return names, calories, receipts


if __name__=='__main__':
    bleu = evaluate.load("bleu")
    rouge = evaluate.load("rouge")

    names, calories, references = original_receipts()
    predictions = gen_receipts( names, calories )

    bleu_result = bleu.compute( predictions = predictions, references = references )
    rouge_result = rouge.compute( predictions = predictions, references = references )

    print("BLEU:", bleu_result)
    print("ROUGE:", rouge_result)
