import json
from http import HTTPStatus

import requests

from service.models.input import CreateOrderRequest
from tests.utils import generate_random_string


def test_users_reach_only_their_own_orders(api_gw_url, order_factory, member_user, member_headers, other_manager_headers):
    # Given: An order of a member
    order = order_factory(member_user, f'{generate_random_string()}-Owner', 2)
    order_url = f'{api_gw_url}/{order["id"]}'

    # When & Then: Another user can't get, delete or list it (not found, like an order that does not exist)
    assert requests.get(order_url, headers=other_manager_headers).status_code == HTTPStatus.NOT_FOUND
    assert requests.delete(order_url, headers=other_manager_headers).status_code == HTTPStatus.NOT_FOUND
    listed = requests.get(api_gw_url, params={'limit': 100}, headers=other_manager_headers)
    assert listed.status_code == HTTPStatus.OK
    assert order['id'] not in {o['id'] for o in json.loads(listed.text)['orders']}

    # And: The owner still gets it, so the delete attempt did not remove it
    assert requests.get(order_url, headers=member_headers).status_code == HTTPStatus.OK


def test_next_token_of_another_user_is_invalid(api_gw_url, order_factory, member_user, member_headers, other_manager_headers):
    # Given: A next_token of a member (two orders and limit=1 guarantee a second page)
    for _ in range(2):
        order_factory(member_user, f'{generate_random_string()}-Owner', 1)
    first = requests.get(api_gw_url, params={'limit': 1}, headers=member_headers)
    next_token = json.loads(first.text)['next_token']
    assert next_token

    # When: Another user lists orders with it
    response = requests.get(api_gw_url, params={'limit': 1, 'next_token': next_token}, headers=other_manager_headers)

    # Then: The token is rejected
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_same_create_request_of_two_users_creates_two_orders(
    api_gw_url, tracked_orders: list[tuple[str, str]], member_user, member_headers, other_manager_user, other_manager_headers
):
    # Given: The same create order body sent by two users (within the idempotency window)
    body = CreateOrderRequest(customer_name=f'{generate_random_string()}-Same', order_item_count=3).model_dump_json()

    # When: Both users create the order
    first = requests.post(api_gw_url, data=body, headers=member_headers)
    second = requests.post(api_gw_url, data=body, headers=other_manager_headers)
    assert first.status_code == HTTPStatus.OK and second.status_code == HTTPStatus.OK
    first_id, second_id = json.loads(first.text)['id'], json.loads(second.text)['id']
    tracked_orders.extend([(member_user.sub, first_id), (other_manager_user.sub, second_id)])

    # Then: Each user gets their own order
    assert first_id != second_id
