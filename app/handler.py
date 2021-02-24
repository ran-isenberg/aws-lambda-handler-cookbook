import json
from json import JSONDecodeError
from typing import Dict


def lambda_handler(event, context):
    try:
        order = json.loads(event['Records'][0]['body'])
        validate(order)
        write_order(order)
    except JSONDecodeError as err:
        print("ERROR: could not parse json body of the message")
        raise err


def validate(order: Dict):
    if not order:
        raise ValueError("ValidationError: order should not be empty")
    # check the structure
    if not {'id', 'description', 'items'}.issubset(order.keys()):
        raise ValueError("ValidationError: malformed metadata")
    # check the value of the items
    for item in order["items"]:
        # here you have to check a lot more fields
        if item["quantity"] < 0:
            raise ValueError("ValidationError: Quantity cant be negative")


def write_order(order):
    pass
