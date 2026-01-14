import json
from datetime import datetime, timezone
from http import HTTPStatus
from typing import Any

from aws_lambda_powertools.utilities.feature_flags.exceptions import SchemaValidationError

from service.dal.dynamo_dal_handler import DynamoDalHandler
from service.models.input import CreateOrderRequest
from tests.utils import generate_api_gw_event, generate_context, generate_random_string

MOCKED_SCHEMA = {
    'features': {
        'premium_features': {
            'default': False,
            'rules': {
                'enable premium features for this specific customer name"': {
                    'when_match': True,
                    'conditions': [{'action': 'EQUALS', 'key': 'customer_name', 'value': 'RanTheBuilder'}],
                }
            },
        },
        'ten_percent_off_campaign': {'default': True},
    },
    'countries': ['ISRAEL', 'USA'],
}


def mock_dynamic_configuration(mocker, mock_schema: dict[str, Any]) -> None:
    """Mock AppConfig Store get_configuration method to use mock schema instead"""
    mocked_get_conf = mocker.patch('aws_lambda_powertools.utilities.parameters.AppConfigProvider.get')
    mocked_get_conf.return_value = mock_schema


def mock_exception_dynamic_configuration(mocker) -> None:
    """Mock AppConfig Store get_configuration method to use mock schema instead"""
    mocker.patch('aws_lambda_powertools.utilities.parameters.AppConfigProvider.get', side_effect=SchemaValidationError('error'))


def call_create_order(body: dict[str, Any]) -> dict[str, Any]:
    # important is done here since idempotency decorator requires an env. variable during import time
    # conf.test sets that env. variable (table name) but it runs after imports
    # this way, idempotency import runs after conftest sets the values already
    from service.handlers.handle_create_order import lambda_handler

    return lambda_handler(body, generate_context())


def test_handler_200_ok(mocker, table_name: str):
    # Given: Dynamic configuration is mocked and a valid order creation request
    mock_dynamic_configuration(mocker, MOCKED_SCHEMA)
    customer_name = f'{generate_random_string()}-RanTheBuilder'
    order_item_count = 5
    body = CreateOrderRequest(customer_name=customer_name, order_item_count=order_item_count)

    # When: The order creation lambda_handler is called
    response = call_create_order(generate_api_gw_event(body.model_dump()))

    # Then: Validate the response and data in DynamoDB table
    assert response['statusCode'] == HTTPStatus.OK
    body_dict = json.loads(response['body'])
    assert body_dict['id']
    assert body_dict['name'] == customer_name
    assert body_dict['item_count'] == 5

    # Use pydynox to verify the item was saved correctly
    db_handler = DynamoDalHandler(table_name)
    OrderEntryModel = db_handler._get_order_model()
    saved_order = OrderEntryModel.get(id=body_dict['id'])
    assert saved_order is not None
    assert saved_order.name == customer_name
    assert saved_order.item_count == order_item_count
    now = int(datetime.now(timezone.utc).timestamp())
    assert now - saved_order.created_at <= 60  # assume item was created in last minute, check that utc time calc is correct


def test_internal_server_error(mocker, table_name: str):
    # Given: Dynamic configuration and a simulated error during DB interaction
    mock_dynamic_configuration(mocker, MOCKED_SCHEMA)

    # Mock pydynox save to raise an exception
    mocker.patch.object(DynamoDalHandler, '_get_order_model', side_effect=Exception('DynamoDB error'))

    body = CreateOrderRequest(customer_name='RanTheBuilder', order_item_count=5)

    # When: The order creation lambda_handler is called
    response = call_create_order(generate_api_gw_event(body.model_dump()))

    # Then: Ensure the response reflects an internal server error
    assert response['statusCode'] == HTTPStatus.INTERNAL_SERVER_ERROR
    body_dict = json.loads(response['body'])
    assert body_dict == {'error': 'internal server error'}


def test_handler_bad_request(mocker):
    # Given: Dynamic configuration is mocked and an invalid order request is prepared
    mock_dynamic_configuration(mocker, MOCKED_SCHEMA)

    # When: The order creation lambda_handler is called with invalid input
    response = call_create_order(generate_api_gw_event({'order_item_count': 5}))

    # Then: Validate the response is a unprocessable entity and error message is correct
    assert response['statusCode'] == HTTPStatus.UNPROCESSABLE_ENTITY
    body_dict = json.loads(response['body'])
    assert body_dict.get('detail') == [{'loc': ['body', 'customer_name'], 'type': 'missing'}]


def test_handler_failed_appconfig_fetch(mocker):
    # Given: Simulated failure during AppConfig fetch and a valid order request
    mock_exception_dynamic_configuration(mocker)
    customer_name = f'{generate_random_string()}-RanTheBuilder'
    order_item_count = 5
    body = CreateOrderRequest(customer_name=customer_name, order_item_count=order_item_count)

    # When: The order creation lambda_handler is called
    response = call_create_order(generate_api_gw_event(body.model_dump()))

    # Then: Validate the response indicates an internal server error and error message
    assert response['statusCode'] == HTTPStatus.INTERNAL_SERVER_ERROR
    body_dict = json.loads(response['body'])
    assert body_dict == {'error': 'internal server error'}
