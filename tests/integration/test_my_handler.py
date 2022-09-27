import json
import os
from http import HTTPStatus
from typing import Any, Dict

import pytest
from aws_lambda_powertools.utilities.feature_flags.exceptions import SchemaValidationError

from cdk.my_service.service_stack.constants import CONFIGURATION_NAME, ENVIRONMENT, POWER_TOOLS_LOG_LEVEL, POWERTOOLS_SERVICE_NAME, SERVICE_NAME
from service.handlers.my_handler import my_handler
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


@pytest.fixture(scope='module', autouse=True)
def init():
    os.environ[POWERTOOLS_SERVICE_NAME] = SERVICE_NAME
    os.environ[POWER_TOOLS_LOG_LEVEL] = 'DEBUG'
    os.environ['REST_API'] = 'https://www.ranthebuilder.cloud/api'
    os.environ['ROLE_ARN'] = 'arn:partition:service:region:account-id:resource-type:resource-id'
    os.environ['CONFIGURATION_APP'] = SERVICE_NAME
    os.environ['CONFIGURATION_ENV'] = ENVIRONMENT
    os.environ['CONFIGURATION_NAME'] = CONFIGURATION_NAME
    os.environ['CONFIGURATION_MAX_AGE_MINUTES'] = '5'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'  # used for appconfig mocked boto calls


def test_handler_200_ok(mocker):

    mock_dynamic_configuration(mocker, MOCKED_SCHEMA)
    body = Input(my_name='RanTheBuilder', order_item_count=5, tier='premium')
    response = my_handler(generate_api_gw_event(body.dict()), generate_context())
    assert response['statusCode'] == HTTPStatus.OK
    body_dict = json.loads(response['body'])
    assert body_dict['success']
    assert body_dict['order_item_count'] == 5


def test_handler_bad_request(mocker):
    mock_dynamic_configuration(mocker, MOCKED_SCHEMA)
    response = my_handler(generate_api_gw_event({'order_item_count': 5}), generate_context())
    assert response['statusCode'] == HTTPStatus.BAD_REQUEST
    body_dict = json.loads(response['body'])
    assert body_dict == {}


def test_handler_failed_appconfig_fetch(mocker):
    mock_exception_dynamic_configuration(mocker)
    response = my_handler(generate_api_gw_event({'order_item_count': 5}), generate_context())
    assert response['statusCode'] == HTTPStatus.INTERNAL_SERVER_ERROR
    body_dict = json.loads(response['body'])
    assert body_dict == {}
