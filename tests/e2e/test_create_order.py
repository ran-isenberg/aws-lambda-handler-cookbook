import json
from http import HTTPStatus

import pytest
import requests

from cdk.my_service.constants import APIGATEWAY, GW_RESOURCE
from service.handlers.schemas.input import Input
from tests.utils import get_stack_output


@pytest.fixture(scope='module', autouse=True)
def api_gw_url():
    return f'{get_stack_output(APIGATEWAY)}api/{GW_RESOURCE}'


def test_handler_200_ok(api_gw_url):
    customer_name = 'RanTheBuilder'
    body = Input(customer_name=customer_name, order_item_count=5)
    response = requests.post(api_gw_url, data=body.json())
    assert response.status_code == HTTPStatus.OK
    body_dict = json.loads(response.text)
    assert body_dict['order_id']
    assert body_dict['customer_name'] == customer_name
    assert body_dict['order_item_count'] == 5


def test_handler_bad_request(api_gw_url):
    body_str = json.dumps({'order_item_count': 5})
    response = requests.post(api_gw_url, data=body_str)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    body_dict = json.loads(response.text)
    assert body_dict == {}
