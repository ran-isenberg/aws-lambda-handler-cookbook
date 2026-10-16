import json
from http import HTTPStatus

from service.models.input import CreateOrderRequest
from tests.conftest import get_order_from_db
from tests.integration.test_create_order import MOCKED_SCHEMA, call_create_order, mock_dynamic_configuration
from tests.integration.test_delete_order import call_delete_order
from tests.integration.test_get_order import call_get_order
from tests.integration.test_list_orders import call_list_orders
from tests.utils import generate_api_gw_event, generate_random_string


def test_get_order_of_another_user_is_not_found(order_factory, writer_user, other_writer_headers):
    # Given: An order of the writer
    order = order_factory(writer_user, f'{generate_random_string()}-Owner', 2)

    # When: Another user gets it by its id
    response = call_get_order(order['id'], other_writer_headers)

    # Then: It is not found, exactly like an order that does not exist
    assert response['statusCode'] == HTTPStatus.NOT_FOUND
    assert json.loads(response['body']) == {'error': 'order was not found'}


def test_delete_order_of_another_user_is_not_found(table_name: str, order_factory, writer_user, other_writer_headers):
    # Given: An order of the writer
    order = order_factory(writer_user, f'{generate_random_string()}-Owner', 2)

    # When: Another user deletes it by its id
    response = call_delete_order(order['id'], other_writer_headers)

    # Then: It is not found, and the order is not deleted
    assert response['statusCode'] == HTTPStatus.NOT_FOUND
    assert get_order_from_db(table_name, writer_user.sub, order['id']) is not None


def test_list_returns_only_the_callers_orders(order_factory, writer_user, writer_headers, other_writer_user, other_writer_headers):
    # Given: Orders of two users
    mine = order_factory(writer_user, f'{generate_random_string()}-Mine', 1)
    theirs = order_factory(other_writer_user, f'{generate_random_string()}-Theirs', 1)

    # When: Each user lists orders
    my_ids = {o['id'] for o in json.loads(call_list_orders(writer_headers, limit=100)['body'])['orders']}
    their_ids = {o['id'] for o in json.loads(call_list_orders(other_writer_headers, limit=100)['body'])['orders']}

    # Then: Each user sees only their own orders
    assert mine['id'] in my_ids and theirs['id'] not in my_ids
    assert theirs['id'] in their_ids and mine['id'] not in their_ids


def test_next_token_of_another_user_is_invalid(order_factory, writer_user, writer_headers, other_writer_headers):
    # Given: A next_token of the writer (two orders and limit=1 guarantee a second page)
    for _ in range(2):
        order_factory(writer_user, f'{generate_random_string()}-Owner', 1)
    next_token = json.loads(call_list_orders(writer_headers, limit=1)['body'])['next_token']
    assert next_token

    # When: Another user lists orders with it
    response = call_list_orders(other_writer_headers, limit=1, next_token=next_token)

    # Then: The token is rejected instead of reading the writer's partition
    assert response['statusCode'] == HTTPStatus.BAD_REQUEST
    assert json.loads(response['body']) == {'error': 'invalid next_token'}


def test_same_create_request_of_two_users_creates_two_orders(
    mocker, tracked_orders: list[tuple[str, str]], writer_user, writer_headers, other_writer_user, other_writer_headers
):
    # Given: The same create order body sent by two users (within the idempotency window)
    mock_dynamic_configuration(mocker, MOCKED_SCHEMA)
    body = CreateOrderRequest(customer_name=f'{generate_random_string()}-Same', order_item_count=3).model_dump()

    # When: Both users create the order
    first = json.loads(call_create_order(generate_api_gw_event(body, writer_headers))['body'])
    tracked_orders.append((writer_user.sub, first['id']))
    second = json.loads(call_create_order(generate_api_gw_event(body, other_writer_headers))['body'])
    tracked_orders.append((other_writer_user.sub, second['id']))

    # Then: The owner is part of the idempotency key, so each user gets their own order
    assert first['id'] != second['id']
