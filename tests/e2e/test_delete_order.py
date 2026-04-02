import json
from http import HTTPStatus

import requests

from service.models.input import CreateOrderRequest
from tests.utils import generate_random_string


def test_handler_200_ok(api_gw_url):
    # Given: An existing order created via POST
    customer_name = f'{generate_random_string()}-RanTheBuilder'
    body = CreateOrderRequest(customer_name=customer_name, order_item_count=5)
    create_response = requests.post(api_gw_url, data=body.model_dump_json())
    assert create_response.status_code == HTTPStatus.OK
    created_order = json.loads(create_response.text)

    # When: Making a DELETE request to the API Gateway URL with the order ID
    response = requests.delete(f'{api_gw_url}/{created_order["id"]}')

    # Then: Validate the response confirms deletion
    assert response.status_code == HTTPStatus.OK
    body_dict = json.loads(response.text)
    assert body_dict['order_id'] == created_order['id']

    # And: Verify the order no longer exists
    get_response = requests.get(f'{api_gw_url}/{created_order["id"]}')
    assert get_response.status_code == HTTPStatus.NOT_FOUND


def test_handler_order_not_found(api_gw_url):
    # Given: A non-existent order ID
    non_existent_id = '00000000-0000-0000-0000-000000000000'

    # When: Making a DELETE request to the API Gateway URL
    response = requests.delete(f'{api_gw_url}/{non_existent_id}')

    # Then: Validate the response status is 404 NOT FOUND
    assert response.status_code == HTTPStatus.NOT_FOUND
