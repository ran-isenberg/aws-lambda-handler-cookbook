import json
import os
from http import HTTPStatus

import pytest

from cdk.aws_lambda_handler_cookbook.service_stack.constants import POWER_TOOLS_LOG_LEVEL, POWERTOOLS_SERVICE_NAME, SERVICE_NAME
from service.handlers.my_handler import my_handler
from service.handlers.schemas.input import Input
from tests.utils import generate_api_gw_event, generate_context


@pytest.fixture(scope='module', autouse=True)
def init():
    os.environ[POWERTOOLS_SERVICE_NAME] = SERVICE_NAME
    os.environ[POWER_TOOLS_LOG_LEVEL] = 'DEBUG'
    os.environ['REST_API'] = 'https://www.ranthebuilder.cloud/api'
    os.environ['ROLE_ARN'] = 'arn:partition:service:region:account-id:resource-type:resource-id'


def test_handler_200_ok():
    body = Input(my_name='RanTheBuilder', order_item_count=5)
    response = my_handler(generate_api_gw_event(body.dict()), generate_context())
    assert response['statusCode'] == HTTPStatus.OK
    body_dict = json.loads(response['body'])
    assert body_dict['message'] == 'success'


def test_handler_bad_request():
    response = my_handler(generate_api_gw_event({'order_item_count': 5}), generate_context())
    assert response['statusCode'] == HTTPStatus.BAD_REQUEST
    body_dict = json.loads(response['body'])
    assert body_dict == {}
