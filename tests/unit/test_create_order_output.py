import uuid

import pytest
from aws_lambda_powertools.utilities.parser import ValidationError

from service.schemas.output import CreateOrderOutput

order_id = str(uuid.uuid4())


def test_invalid_items_type():
    with pytest.raises(ValidationError):
        CreateOrderOutput(order_id=order_id, customer_name='3333', order_item_count='a')


def test_invalid_items_negative():
    with pytest.raises(ValidationError):
        CreateOrderOutput(order_id=order_id, customer_name='3333', order_item_count=-1)


def test_invalid_items_zero():
    with pytest.raises(ValidationError):
        CreateOrderOutput(order_id=order_id, customer_name='3333', order_item_count=0)


def test_invalid_order_id():
    with pytest.raises(ValidationError):
        CreateOrderOutput(order_id='2', customer_name='3333', order_item_count=2)


def test_valid_output():
    CreateOrderOutput(customer_name='222', order_item_count=4, order_id=order_id)
