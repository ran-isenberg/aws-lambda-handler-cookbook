import json
from http import HTTPStatus

import requests

from service.models.input import CreateOrderRequest
from tests.utils import generate_random_string


def test_handler_200_ok(api_gw_url):
    # Given: A valid order request payload
    customer_name = f'{generate_random_string()}-RanTheBuilder'
    body = CreateOrderRequest(customer_name=customer_name, order_item_count=5)

    # When: Making a POST request to the API Gateway URL
    response = requests.post(api_gw_url, data=body.model_dump_json())

    # Then: Validate the response and its body with expected values
    assert response.status_code == HTTPStatus.OK
    body_dict = json.loads(response.text)
    assert body_dict['id']
    assert body_dict['name'] == customer_name
    assert body_dict['item_count'] == 5

    # Given: The ID of the original order
    original_order_id = body_dict['id']

    # When: Sending the same request (testing idempotency)
    response = requests.post(api_gw_url, data=body.model_dump_json())

    # Then: Validate that the new order ID is same as the original order ID
    assert response.status_code == HTTPStatus.OK
    body_dict = json.loads(response.text)
    assert body_dict['id'] == original_order_id


def test_handler_bad_request(api_gw_url):
    # Given: A malformed request payload (bad request), missing name
    body_str = json.dumps({'order_item_count': 5})

    # When: Making a POST request to the API Gateway URL
    response = requests.post(api_gw_url, data=body_str)

    # Then: Validate the response status is 422 UNPROCESSABLE_ENTITY
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
