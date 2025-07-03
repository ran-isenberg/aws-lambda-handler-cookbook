import json
import uuid
from typing import Any, Dict
from unittest.mock import patch

import boto3
import pytest
from botocore.stub import Stubber
from mypy_boto3_dynamodb.service_resource import Table

from service.dal import DynamoDalHandler
from service.handlers.handle_delete_order import lambda_handler
from service.models.exceptions import OrderNotFoundException, InternalServerException


def call_delete_order(body: Dict[str, Any]) -> Dict[str, Any]:
    event = {
        'body': json.dumps(body),
        'httpMethod': 'POST',
        'path': '/api/orders/delete',
        'requestContext': {'requestId': '227b78aa-779d-47d4-a48a-e83c31501c64'},
    }
    response = lambda_handler(event=event, context=None)
    return response


def test_handler_200_ok(mocker, table_name: str):
    # Create a real order in DynamoDB
    order_id = str(uuid.uuid4())
    customer_name = "Integration Test Customer"
    item_count = 10
    
    # Create the item to be used in tests
    table: Table = boto3.resource('dynamodb').Table(table_name)
    table.put_item(
        Item={
            'id': order_id,
            'name': customer_name,
            'item_count': item_count,
            'created_at': 1234567890,
        }
    )

    # Call delete order handler
    result = call_delete_order({'order_id': order_id})

    # Verify the response
    assert result['statusCode'] == 200
    assert json.loads(result['body'])['id'] == order_id
    assert json.loads(result['body'])['name'] == customer_name
    assert json.loads(result['body'])['item_count'] == item_count

    # Verify the item was actually deleted
    response = table.get_item(Key={'id': order_id})
    assert 'Item' not in response


def test_handler_404_not_found(mocker, table_name: str):
    # Use a UUID that doesn't exist
    order_id = str(uuid.uuid4())
    
    # Call delete order handler for non-existent order
    result = call_delete_order({'order_id': order_id})

    # Verify the response
    assert result['statusCode'] == 404
    assert json.loads(result['body'])['error'] == 'order not found'


def test_internal_server_error(mocker, table_name: str):
    # Mock DynamoDB client to simulate a ClientError
    order_id = str(uuid.uuid4())
    
    # Get the table
    table: Table = boto3.resource('dynamodb').Table(table_name)
    
    with Stubber(table.meta.client) as stubber:
        # Stub the get_item method to raise an exception
        stubber.add_client_error('get_item', service_error_code='InternalServerError')
        
        # Mock get_db_handler to return our stubbed table
        mocker.patch.object(DynamoDalHandler, '_get_db_handler', return_value=table)
        
        # Call delete order with the stubbed client
        result = call_delete_order({'order_id': order_id})
        
        # Verify the response
        assert result['statusCode'] == 501
        assert json.loads(result['body'])['error'] == 'internal server error'