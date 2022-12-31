import json
from http import HTTPStatus
from typing import Any, Dict

from aws_lambda_powertools.utilities.feature_flags.exceptions import SchemaValidationError
from botocore.exceptions import ClientError

from service.handlers.create_order import create_order
from service.handlers.schemas.input import Input
from tests.utils import generate_api_gw_event, generate_context

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


def test_handler_200_ok(mocker):
    mock_dynamic_configuration(mocker, MOCKED_SCHEMA)
    customer_name = 'RanTheBuilder'
    body = Input(customer_name=customer_name, order_item_count=5, tier='premium')
    response = create_order(generate_api_gw_event(body.dict()), generate_context())
    assert response['statusCode'] == HTTPStatus.OK
    body_dict = json.loads(response['body'])
    assert body_dict['order_id']
    assert body_dict['customer_name'] == customer_name
    assert body_dict['order_item_count'] == 5


def test_internal_server_error(mocker):

    def db_mock_function(table_name: str):
        raise ClientError(error_response={}, operation_name='put_item')

    db_mock = mocker.patch('service.logic.handle_create_request._get_db_handler')
    db_mock.side_effect = db_mock_function
    body = Input(customer_name='RanTheBuilder', order_item_count=5, tier='premium')
    response = create_order(generate_api_gw_event(body.dict()), generate_context())
    assert response['statusCode'] == HTTPStatus.INTERNAL_SERVER_ERROR
    db_mock.assert_called


def test_handler_bad_request(mocker):
    mock_dynamic_configuration(mocker, MOCKED_SCHEMA)
    response = create_order(generate_api_gw_event({'order_item_count': 5}), generate_context())
    assert response['statusCode'] == HTTPStatus.BAD_REQUEST
    body_dict = json.loads(response['body'])
    assert body_dict == {}


def test_handler_failed_appconfig_fetch(mocker):
    mock_exception_dynamic_configuration(mocker)
    response = create_order(generate_api_gw_event({'order_item_count': 5}), generate_context())
    assert response['statusCode'] == HTTPStatus.INTERNAL_SERVER_ERROR
    body_dict = json.loads(response['body'])
    assert body_dict == {}
