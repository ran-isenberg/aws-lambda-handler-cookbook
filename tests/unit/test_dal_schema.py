import uuid

import pytest
from aws_lambda_powertools.utilities.parser import ValidationError

from service.dal.schemas.db import OrderEntry

order_id = str(uuid.uuid4())


def test_invalid_items_type():
    # Given: An invalid non-integer order_item_count
    customer_name = '3333'
    order_item_count = 'a'

    # When & Then: OrderEntry is initialized, expect a ValidationError
    with pytest.raises(ValidationError):
        OrderEntry(order_id=order_id, customer_name=customer_name, order_item_count=order_item_count)


def test_invalid_items_negative():
    # Given: An invalid negative order_item_count
    customer_name = '3333'
    order_item_count = -1

    # When & Then: OrderEntry is initialized, expect a ValidationError
    with pytest.raises(ValidationError):
        OrderEntry(order_id=order_id, customer_name=customer_name, order_item_count=order_item_count)


def test_invalid_items_zero():
    # Given: An invalid zero order_item_count
    customer_name = '3333'
    order_item_count = 0

    # When & Then: OrderEntry is initialized, expect a ValidationError
    with pytest.raises(ValidationError):
        OrderEntry(order_id=order_id, customer_name=customer_name, order_item_count=order_item_count)


def test_invalid_order_id():
    # Given: An invalid order_id
    order_id_invalid = '2'
    customer_name = '3333'
    order_item_count = 2

    # When & Then: OrderEntry is initialized, expect a ValidationError
    with pytest.raises(ValidationError):
        OrderEntry(order_id=order_id_invalid, customer_name=customer_name, order_item_count=order_item_count)


def test_valid_output():
    # Given: Valid inputs
    customer_name = '222'
    order_item_count = 4

    # When: OrderEntry is initialized
    # Then: No exception should be raised
    OrderEntry(order_id=order_id, customer_name=customer_name, order_item_count=order_item_count)
