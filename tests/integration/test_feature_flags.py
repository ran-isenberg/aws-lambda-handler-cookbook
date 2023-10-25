import json
from http import HTTPStatus
from typing import Any

from service.models.input import CreateOrderRequest
from tests.utils import generate_api_gw_event, generate_context, generate_random_string

MOCKED_SCHEMA_CAMPAIGN_ON = {
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

MOCKED_SCHEMA_CAMPAIGN_OFF = {
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
        'ten_percent_off_campaign': {'default': False},
    },
    'countries': ['ISRAEL', 'USA'],
}


def mock_dynamic_configuration(mocker, mock_schema: dict[str, Any]) -> None:
    """Mock AppConfig Store get_configuration method to use mock schema instead"""
    mocked_get_conf = mocker.patch('aws_lambda_powertools.utilities.parameters.AppConfigProvider.get')
    mocked_get_conf.return_value = mock_schema


def call_create_order(body: dict[str, Any]) -> dict[str, Any]:
    # important is done here since idempotency decorator requires an env. variable during import time
    # conf.test sets that env. variable (table name) but it runs after imports
    # this way, idempotency import runs after conftest sets the values already
    from service.handlers.handle_create_order import lambda_handler

    return lambda_handler(body, generate_context())


def assert_response(response: dict[str, Any], expected_response_code: HTTPStatus, expected_customer_name: str, expected_order_item_count: int):
    # assert response
    assert response['statusCode'] == expected_response_code
    body_dict = json.loads(response['body'])
    assert body_dict['id']
    assert body_dict['name'] == expected_customer_name
    assert body_dict['item_count'] == expected_order_item_count


def spy_on_campaign_logic(mocker):
    import service.logic.create_order as cr

    return mocker.spy(cr, 'handle_campaign')


def spy_on_premium_logic(mocker):
    import service.logic.create_order as cr

    return mocker.spy(cr, 'apply_premium_user_discount')


def test_handler_campaign_on_200_ok(mocker):
    # Given: A mocked dynamic configuration with campaign ON and a valid order request.
    mock_dynamic_configuration(mocker, MOCKED_SCHEMA_CAMPAIGN_ON)
    campaign_logic_spy = spy_on_campaign_logic(mocker)
    customer_name = f'{generate_random_string()}-RanTheBuilder'
    order_item_count = 5
    body = CreateOrderRequest(customer_name=customer_name, order_item_count=order_item_count)

    # When: The order creation lambda_handler is called
    response = call_create_order(generate_api_gw_event(body.model_dump()))

    # Then: Validate the response and ensure the campaign logic was executed.
    assert_response(response, HTTPStatus.OK, customer_name, order_item_count)
    assert campaign_logic_spy.call_count == 1


def test_handler_campaign_off_200_ok(mocker):
    # Given: A mocked dynamic configuration with campaign OFF and a valid order request.
    mock_dynamic_configuration(mocker, MOCKED_SCHEMA_CAMPAIGN_OFF)
    campaign_logic_spy = spy_on_campaign_logic(mocker)
    customer_name = f'{generate_random_string()}-NoCampaignForYou'
    order_item_count = 5
    body = CreateOrderRequest(customer_name=customer_name, order_item_count=order_item_count)

    # When: The order creation lambda_handler is called
    response = call_create_order(generate_api_gw_event(body.model_dump()))

    # Then: Validate the response and ensure the campaign logic was not executed.
    assert_response(response, HTTPStatus.OK, customer_name, order_item_count)
    assert campaign_logic_spy.call_count == 0


def test_handler_premium_on_200_ok(mocker, monkeypatch):
    # Given: A mocked dynamic configuration with premium ON and a valid order request.
    mock_dynamic_configuration(mocker, MOCKED_SCHEMA_CAMPAIGN_ON)
    # Set POWERTOOLS_IDEMPOTENCY_DISABLED before calling decorated functions
    monkeypatch.setenv('POWERTOOLS_IDEMPOTENCY_DISABLED', 1)
    premium_logic_spy = spy_on_premium_logic(mocker)
    customer_name = 'RanTheBuilder'
    order_item_count = 6
    body = CreateOrderRequest(customer_name=customer_name, order_item_count=order_item_count)

    # When: The order creation lambda_handler is called
    response = call_create_order(generate_api_gw_event(body.model_dump()))

    # Then: Validate the response and ensure the premium logic was executed.
    assert_response(response, HTTPStatus.OK, customer_name, order_item_count)
    assert premium_logic_spy.call_count == 1


def test_handler_premium_off_200_ok(mocker):
    # Given: A mocked dynamic configuration with premium OFF and a valid order request.
    mock_dynamic_configuration(mocker, MOCKED_SCHEMA_CAMPAIGN_ON)
    premium_logic_spy = spy_on_premium_logic(mocker)
    customer_name = f'{generate_random_string()}-NoCampaignForYou'
    order_item_count = 5
    body = CreateOrderRequest(customer_name=customer_name, order_item_count=order_item_count)

    # When: The order creation lambda_handler is called
    response = call_create_order(generate_api_gw_event(body.model_dump()))

    # Then: Validate the response and ensure the premium logic was not executed.
    assert_response(response, HTTPStatus.OK, customer_name, order_item_count)
    assert premium_logic_spy.call_count == 0
