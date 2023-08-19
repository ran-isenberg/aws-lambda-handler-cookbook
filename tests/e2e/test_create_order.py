import json
from http import HTTPStatus

import pytest
import requests

from cdk.service.constants import APIGATEWAY, GW_RESOURCE
from service.schemas.input import CreateOrderRequest
from tests.utils import generate_random_string, get_stack_output


@pytest.fixture(scope='module', autouse=True)
def api_gw_url():
    return f'{get_stack_output(APIGATEWAY)}api/{GW_RESOURCE}'


def test_handler_200_ok(api_gw_url):
    customer_name = f'{generate_random_string()}-RanTheBuilder'
    body = CreateOrderRequest(customer_name=customer_name, order_item_count=5)
    response = requests.post(api_gw_url, data=body.model_dump_json())
    assert response.status_code == HTTPStatus.OK
    body_dict = json.loads(response.text)
    assert body_dict['order_id']
    assert body_dict['customer_name'] == customer_name
    assert body_dict['order_item_count'] == 5

    # check idempotency, send same request
    original_order_id = body_dict['order_id']
    response = requests.post(api_gw_url, data=body.model_dump_json())
    assert response.status_code == HTTPStatus.OK
    body_dict = json.loads(response.text)
    assert body_dict['order_id'] == original_order_id


def test_handler_bad_request(api_gw_url):
    body_str = json.dumps({'order_item_count': 5})
    response = requests.post(api_gw_url, data=body_str)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    body_dict = json.loads(response.text)
    assert body_dict == {}
