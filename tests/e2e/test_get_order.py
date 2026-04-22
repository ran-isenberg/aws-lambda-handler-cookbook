import json
from http import HTTPStatus

import requests

from tests.utils import generate_random_string


def test_handler_200_ok(api_gw_url, order_factory):
    # Given: An existing order
    customer_name = f'{generate_random_string()}-RanTheBuilder'
    created_order = order_factory(customer_name, 5)

    # When: Making a GET request to the API Gateway URL with the order ID
    response = requests.get(f'{api_gw_url}/{created_order["id"]}')

    # Then: Validate the response contains the correct order data
    assert response.status_code == HTTPStatus.OK
    body_dict = json.loads(response.text)
    assert body_dict['id'] == created_order['id']
    assert body_dict['name'] == customer_name
    assert body_dict['item_count'] == 5


def test_handler_order_not_found(api_gw_url):
    # Given: A non-existent order ID
    non_existent_id = '00000000-0000-0000-0000-000000000000'

    # When: Making a GET request to the API Gateway URL
    response = requests.get(f'{api_gw_url}/{non_existent_id}')

    # Then: Validate the response status is 404 NOT FOUND
    assert response.status_code == HTTPStatus.NOT_FOUND
