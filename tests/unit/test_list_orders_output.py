import uuid

import pytest
from aws_lambda_powertools.utilities.parser import ValidationError

from service.models.output import ListOrdersOutput


def _order(name: str = '333', item_count: int = 4) -> dict:
    return {'id': str(uuid.uuid4()), 'name': name, 'item_count': item_count}


def test_valid_empty_list():
    # Given: An empty orders list
    # When: ListOrdersOutput is initialized
    output = ListOrdersOutput(orders=[])

    # Then: The orders list is empty and next_token defaults to None
    assert output.orders == []
    assert output.next_token is None


def test_valid_non_empty_list_with_next_token():
    # Given: Two valid orders and a next_token
    orders = [_order(), _order(name='Alice', item_count=2)]

    # When: ListOrdersOutput is initialized
    output = ListOrdersOutput(orders=orders, next_token='opaque-cursor')

    # Then: Both orders and the next_token are preserved
    assert len(output.orders) == 2
    assert output.orders[1].name == 'Alice'
    assert output.orders[1].item_count == 2
    assert output.next_token == 'opaque-cursor'


def test_invalid_item_count_propagates():
    # Given: An invalid item_count inside an order
    orders = [_order(item_count=0)]

    # When & Then: ListOrdersOutput raises a validation error from the nested Order
    with pytest.raises(ValidationError):
        ListOrdersOutput(orders=orders)


def test_invalid_id_propagates():
    # Given: An invalid id inside an order
    orders = [{'id': 'not-a-uuid', 'name': 'x', 'item_count': 1}]

    # When & Then: ListOrdersOutput raises a validation error from the nested Order
    with pytest.raises(ValidationError):
        ListOrdersOutput(orders=orders)
