import json
from http import HTTPStatus

import requests

from cdk.aws_lambda_handler_cookbook.service_stack.constants import APIGATEWAY, GW_RESOURCE
from tests.utils import get_stack_output


def test_handler_200_ok():
    api_gw_url = get_stack_output(APIGATEWAY)
    response = requests.get(f'{api_gw_url}/api/{GW_RESOURCE}', headers={})
    assert response.status_code == HTTPStatus.OK
    body_dict = json.loads(response.text)
    assert body_dict['message'] == 'success'
