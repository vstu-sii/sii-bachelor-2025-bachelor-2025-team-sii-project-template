import os
import sys
import json
sys.path.append("../models")
import evaluate
from baseline import *


def gen_receipts( model_name, names, calories ):
    m = Model( model_name )
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
    init_module()

    bleu = evaluate.load("bleu")
    rouge = evaluate.load("rouge")

    names, calories, references = original_receipts()
    predictions_b = gen_receipts( "TinyLlama/TinyLlama-1.1B-Chat-v1.0", names, calories )
    predictions_a = gen_receipts( "LiquidAI/LFM2-1.2B", names, calories )

    for predictions in [predictions_a, predictions_b]:
        bleu_result = bleu.compute( predictions = predictions, references = references )
        rouge_result = rouge.compute( predictions = predictions, references = references )

        print('-' * 80)
        print("BLEU:", bleu_result)
        print("ROUGE:", rouge_result)
