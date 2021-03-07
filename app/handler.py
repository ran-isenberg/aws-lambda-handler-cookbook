import json
from json import JSONDecodeError
from typing import Dict
from uuid import UUID

def lambda_handler(event: Dict, context) -> None:
    # validate input
    validate(event)
    # process validated data
    write_order(event)


def _validate_order_item(items: Dict) -> None:
    # check the value of the items
    if not items:
        raise ValueError("ValidationError: order items should not be empty")
    for item in items:
        if not {'type', 'id', 'quantity', 'description'}.issubset(item.keys()):
            raise ValueError("ValidationError: malformed item")
            # here you have to check a lot more fields
        if item["quantity"] <= 0:
            raise ValueError("ValidationError: quantity cant be negative or zero")
        UUID(item["id"]) # raises value error in case of invalid UUID format
        if item["type"] not in ["ACCESSORIES", "COMPUTER"]:
            raise ValueError(f'ValidationError: invalid item type, type={item["type"]}') 

def validate(event: Dict) -> None:
    if not event or event is None:
        raise ValueError("event should not be empty")
    records = event.get('Records',[])
    if not records:
        raise ValueError("ValidationError: orders should not be empty")
    for record in records:
        try: 
            order: Dict = json.loads(record['body'])
        except (IndexError, KeyError, JSONDecodeError) as err:
            raise ValueError('ValidationError: invalid order body, unable to decode')
        # check the structure
        if not {'id', 'description', 'items'}.issubset(order.keys()):
            raise ValueError("ValidationError: malformed order metadata")
        UUID(order["id"]) # raises value error in case of invalid UUID format
        
        _validate_order_item(order.get("items", {}))


def write_order(order: Dict):
    pass
