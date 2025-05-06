import json
from unittest.mock import MagicMock, patch

import pytest
from aws_lambda_powertools.event_handler.openapi.params import Path

from service.handlers.handle_delete_order import handle_delete_order, lambda_handler
from service.models.input import DeleteOrderRequest
from service.models.output import DeleteOrderOutput


@patch('service.handlers.handle_delete_order.delete_order')
@patch('service.handlers.handle_delete_order.app')
@patch('service.handlers.handle_delete_order.get_environment_variables')
@patch('service.handlers.handle_delete_order.parse_configuration')
def test_handle_delete_order_success(mock_parse_config, mock_get_env_vars, mock_app, mock_delete_order):
    # Setup
    order_id = "12345678-1234-1234-1234-123456789012"
    mock_env_vars = MagicMock()
    mock_env_vars.TABLE_NAME = "test-table"
    mock_get_env_vars.return_value = mock_env_vars
    
    # Set up the expected return value from delete_order
    expected_output = DeleteOrderOutput(id=order_id, name="Test Customer", item_count=5)
    mock_delete_order.return_value = expected_output
    
    # Execute
    result = handle_delete_order(order_id=order_id)
    
    # Verify
    assert result == expected_output
    
    # Check that delete_order was called with correct parameters
    mock_delete_order.assert_called_once()
    called_args = mock_delete_order.call_args.kwargs
    assert isinstance(called_args['delete_request'], DeleteOrderRequest)
    assert called_args['delete_request'].order_id == order_id
    assert called_args['table_name'] == mock_env_vars.TABLE_NAME
    assert called_args['context'] == mock_app.lambda_context


@patch('service.handlers.handle_delete_order.app')
def test_lambda_handler(mock_app):
    # Setup
    event = {'some': 'event'}
    context = {'some': 'context'}
    mock_app.resolve.return_value = {'some': 'response'}
    
    # Execute
    response = lambda_handler(event=event, context=context)
    
    # Verify
    mock_app.resolve.assert_called_once_with(event, context)
    assert response == {'some': 'response'}