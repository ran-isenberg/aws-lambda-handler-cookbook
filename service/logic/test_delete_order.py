import uuid
from unittest.mock import MagicMock, patch

import pytest
from aws_lambda_powertools.utilities.idempotency import IdempotencyConfig, idempotency_function
from aws_lambda_powertools.utilities.typing import LambdaContext

from service.dal.db_handler import DalHandler
from service.logic.delete_order import delete_order
from service.models.input import DeleteOrderRequest
from service.models.order import Order
from service.models.output import DeleteOrderOutput


@pytest.fixture
def lambda_context():
    return MagicMock(spec=LambdaContext)


@pytest.fixture
def mock_dal_handler():
    dal_handler = MagicMock(spec=DalHandler)
    return dal_handler


@pytest.fixture
def delete_request():
    return DeleteOrderRequest(order_id="12345678-1234-1234-1234-123456789012")


@patch('service.logic.delete_order.idempotent_function')
@patch('service.logic.delete_order.get_dal_handler')
def test_successful_delete_order(mock_get_dal_handler, mock_idempotent, mock_dal_handler, delete_request, lambda_context):
    # Setup
    # Mock idempotent_function decorator to call the function directly
    mock_idempotent.side_effect = lambda *args, **kwargs: kwargs.get('data_keyword_argument') and idempotency_function(**kwargs) or args[0]
    
    # Mock the DAL handler to return an order
    mock_order = Order(id=delete_request.order_id, name="Test Customer", item_count=5)
    mock_dal_handler.delete_order.return_value = mock_order
    mock_get_dal_handler.return_value = mock_dal_handler
    
    # Execute
    result = delete_order(delete_request=delete_request, table_name="test-table", context=lambda_context)
    
    # Verify
    assert result.id == mock_order.id
    assert result.name == mock_order.name
    assert result.item_count == mock_order.item_count
    
    # Check that the DAL handler was called with the correct order ID
    mock_dal_handler.delete_order.assert_called_once_with(order_id=delete_request.order_id)


@patch('service.logic.delete_order.idempotent_function')
@patch('service.logic.delete_order.get_dal_handler')
def test_delete_order_not_found(mock_get_dal_handler, mock_idempotent, mock_dal_handler, delete_request, lambda_context):
    # Setup
    # Mock idempotent_function decorator to call the function directly
    mock_idempotent.side_effect = lambda *args, **kwargs: kwargs.get('data_keyword_argument') and idempotency_function(**kwargs) or args[0]
    
    # Mock the DAL handler to return None, indicating no order was found
    mock_dal_handler.delete_order.return_value = None
    mock_get_dal_handler.return_value = mock_dal_handler
    
    # Execute
    result = delete_order(delete_request=delete_request, table_name="test-table", context=lambda_context)
    
    # Verify
    assert result.id == delete_request.order_id
    assert result.name == "Order not found"
    assert result.item_count == 0
    
    # Check that the DAL handler was called with the correct order ID
    mock_dal_handler.delete_order.assert_called_once_with(order_id=delete_request.order_id)