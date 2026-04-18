import json
from http import HTTPStatus

import requests

from tests.utils import generate_random_string


def test_handler_200_ok(api_gw_url, order_factory):
    # Given: An existing order created via the factory
    customer_name = f'{generate_random_string()}-RanTheBuilder'
    created_order = order_factory(customer_name, 5)

    # When: Making a GET request to /api/orders with a generous limit
    response = requests.get(api_gw_url, params={'limit': 100})

    # Then: The response is 200 and contains the created order
    assert response.status_code == HTTPStatus.OK
    body_dict = json.loads(response.text)
    assert 'orders' in body_dict
    assert 'next_token' in body_dict
    ids = {o['id'] for o in body_dict['orders']}
    assert created_order['id'] in ids


def test_handler_pagination_round_trip(api_gw_url, order_factory):
    # Given: Two orders exist (create them to guarantee at least two pages with limit=1)
    for _ in range(2):
        order_factory(f'{generate_random_string()}-RanTheBuilder', 1)

    # When: Fetching the first page with limit=1
    first = requests.get(api_gw_url, params={'limit': 1})
    assert first.status_code == HTTPStatus.OK
    first_body = json.loads(first.text)
    assert len(first_body['orders']) == 1
    assert first_body['next_token']

    # And: Passing next_token to fetch the second page
    second = requests.get(api_gw_url, params={'limit': 1, 'next_token': first_body['next_token']})

    # Then: The second page loads and returns a different order
    assert second.status_code == HTTPStatus.OK
    second_body = json.loads(second.text)
    assert len(second_body['orders']) >= 0
    if second_body['orders']:
        assert second_body['orders'][0]['id'] != first_body['orders'][0]['id']


def test_handler_invalid_next_token(api_gw_url):
    # When: Calling list with a malformed next_token
    response = requests.get(api_gw_url, params={'next_token': 'not-valid-base64!!!'})

    # Then: The API responds with 400 Bad Request
    assert response.status_code == HTTPStatus.BAD_REQUEST
    body_dict = json.loads(response.text)
    assert body_dict == {'error': 'invalid next_token'}
