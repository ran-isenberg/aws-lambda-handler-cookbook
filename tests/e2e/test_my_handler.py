import json
from http import HTTPStatus

import requests

from cdk.my_service.service_stack.constants import APIGATEWAY, GW_RESOURCE
from service.handlers.schemas.input import Input
from tests.utils import get_stack_output


def test_handler_200_ok():
    body = Input(my_name='RanTheBuilder', order_item_count=5)
    api_gw_url = get_stack_output(APIGATEWAY)
    response = requests.post(f'{api_gw_url}/api/{GW_RESOURCE}', data=body.json())
    assert response.status_code == HTTPStatus.OK
    body_dict = json.loads(response.text)
    assert body_dict['success']
    assert body_dict['order_item_count'] == 5


def test_handler_bad_request():
    body_str = json.dumps({'order_item_count': 5})
    api_gw_url = get_stack_output(APIGATEWAY)
    response = requests.post(f'{api_gw_url}/api/{GW_RESOURCE}', data=body_str)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    body_dict = json.loads(response.text)
    assert body_dict == {}
