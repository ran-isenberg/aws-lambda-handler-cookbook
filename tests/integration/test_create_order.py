import json
from http import HTTPStatus
from typing import Any, Dict

import boto3
from aws_lambda_powertools.utilities.feature_flags.exceptions import SchemaValidationError
from botocore.stub import Stubber

from service.dal.dynamo_dal_handler import DynamoDalHandler
from service.schemas.input import CreateOrderRequest
from tests.utils import generate_api_gw_event, generate_context, generate_random_string

MOCKED_SCHEMA = {
    'features': {
        'premium_features': {
            'default': False,
            'rules': {
                'enable premium features for this specific customer name"': {
                    'when_match': True,
                    'conditions': [{
                        'action': 'EQUALS',
                        'key': 'customer_name',
                        'value': 'RanTheBuilder'
                    }]
                }
            }
        },
        'ten_percent_off_campaign': {
            'default': True
        }
    },
    'countries': ['ISRAEL', 'USA']
}


def mock_dynamic_configuration(mocker, mock_schema: Dict[str, Any]) -> None:
    """Mock AppConfig Store get_configuration method to use mock schema instead"""
    mocked_get_conf = mocker.patch('aws_lambda_powertools.utilities.parameters.AppConfigProvider.get')
    mocked_get_conf.return_value = mock_schema


def mock_exception_dynamic_configuration(mocker) -> None:
    """Mock AppConfig Store get_configuration method to use mock schema instead"""
    mocker.patch('aws_lambda_powertools.utilities.parameters.AppConfigProvider.get', side_effect=SchemaValidationError('error'))


def call_create_order(body: Dict[str, Any]) -> Dict[str, Any]:
    # important is done here since idempotency decorator requires an env. variable during import time
    # conf.test sets that env. variable (table name) but it runs after imports
    # this way, idempotency import runs after conftest sets the values already
    from service.handlers.create_order import create_order
    return create_order(body, generate_context())


def test_handler_200_ok(mocker, table_name: str):
    mock_dynamic_configuration(mocker, MOCKED_SCHEMA)
    customer_name = f'{generate_random_string()}-RanTheBuilder'
    order_item_count = 5
    body = CreateOrderRequest(customer_name=customer_name, order_item_count=order_item_count)
    response = call_create_order(generate_api_gw_event(body.model_dump()))
    # assert response
    assert response['statusCode'] == HTTPStatus.OK
    body_dict = json.loads(response['body'])
    assert body_dict['order_id']
    assert body_dict['customer_name'] == customer_name
    assert body_dict['order_item_count'] == 5
    # assert side effect - DynamoDB table
    dynamodb_table = boto3.resource('dynamodb').Table(table_name)
    response = dynamodb_table.get_item(Key={'order_id': body_dict['order_id']})
    assert 'Item' in response  # order was found
    assert response['Item']['customer_name'] == customer_name
    assert response['Item']['order_item_count'] == order_item_count


def test_internal_server_error(mocker):
    mock_dynamic_configuration(mocker, MOCKED_SCHEMA)
    db_handler: DynamoDalHandler = DynamoDalHandler('table')
    table = db_handler._get_db_handler()
    stubber = Stubber(table.meta.client)
    stubber.add_client_error(method='put_item', service_error_code='ValidationException')
    stubber.activate()
    body = CreateOrderRequest(customer_name='RanTheBuilder', order_item_count=5)
    response = call_create_order(generate_api_gw_event(body.model_dump()))
    assert response['statusCode'] == HTTPStatus.INTERNAL_SERVER_ERROR
    stubber.deactivate()
    DynamoDalHandler._instances = {}


def test_handler_bad_request(mocker):
    mock_dynamic_configuration(mocker, MOCKED_SCHEMA)
    response = call_create_order(generate_api_gw_event({'order_item_count': 5}))
    assert response['statusCode'] == HTTPStatus.BAD_REQUEST
    body_dict = json.loads(response['body'])
    assert body_dict == {}


def test_handler_failed_appconfig_fetch(mocker):
    mock_exception_dynamic_configuration(mocker)
    customer_name = f'{generate_random_string()}-RanTheBuilder'
    order_item_count = 5
    body = CreateOrderRequest(customer_name=customer_name, order_item_count=order_item_count)
    response = call_create_order(generate_api_gw_event(body.model_dump()))
    assert response['statusCode'] == HTTPStatus.INTERNAL_SERVER_ERROR
    body_dict = json.loads(response['body'])
    assert body_dict == {}
