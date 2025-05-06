import json
import uuid
from typing import Dict
from unittest.mock import MagicMock, patch

import pytest
from aws_lambda_powertools.utilities.typing import LambdaContext

from service.handlers.handle_delete_order import lambda_handler
from service.models.exceptions import OrderNotFoundException
from service.models.order import Order


@pytest.fixture
def lambda_context():
    return MagicMock(spec=LambdaContext)


@pytest.fixture
def order_id():
    return str(uuid.uuid4())


@pytest.fixture
def delete_event(order_id):
    return {
        'body': json.dumps({'order_id': order_id}),
        'httpMethod': 'POST',
        'path': '/api/orders/delete',
        'requestContext': {'requestId': '227b78aa-779d-47d4-a48a-e83c31501c64'},
    }


def test_delete_order_handler_success(delete_event, lambda_context, monkeypatch):
    # Mock environment variables
    monkeypatch.setenv('TABLE_NAME', 'test_table')

    order_id = json.loads(delete_event['body'])['order_id']
    order = Order(id=order_id, name="Test Customer", item_count=5)

    # Mock delete_order function
    with patch('service.handlers.handle_delete_order.delete_order') as mock_delete_order:
        mock_delete_order.return_value = order

        # Invoke the handler
        result = lambda_handler(delete_event, lambda_context)

        # Verify the expected behavior
        assert result['statusCode'] == 200
        assert json.loads(result['body'])['id'] == order_id
        mock_delete_order.assert_called_once()


def test_delete_order_handler_not_found(delete_event, lambda_context, monkeypatch):
    # Mock environment variables
    monkeypatch.setenv('TABLE_NAME', 'test_table')

    # Mock delete_order function to raise OrderNotFoundException
    with patch('service.handlers.handle_delete_order.delete_order') as mock_delete_order:
        mock_delete_order.side_effect = OrderNotFoundException("Order not found")

        # Invoke the handler
        result = lambda_handler(delete_event, lambda_context)

        # Verify the expected behavior
        assert result['statusCode'] == 404
        assert json.loads(result['body'])['error'] == 'order not found'