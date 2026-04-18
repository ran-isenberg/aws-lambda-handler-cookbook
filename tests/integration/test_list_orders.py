import json
from http import HTTPStatus

from tests.utils import generate_api_gw_event_with_path_params, generate_context, generate_random_string


def call_list_orders(limit: int | None = None, next_token: str | None = None) -> dict:
    from service.handlers.handle_list_orders import lambda_handler

    event = generate_api_gw_event_with_path_params(
        http_method='GET',
        path='/api/orders',
        path_parameters=None,
    )
    query: dict[str, str] = {}
    if limit is not None:
        query['limit'] = str(limit)
    if next_token is not None:
        query['next_token'] = next_token
    event['queryStringParameters'] = query or None
    event['multiValueQueryStringParameters'] = {k: [v] for k, v in query.items()} or None
    return lambda_handler(event, generate_context())


def test_handler_200_ok_single_page(order_factory):
    # Given: Two existing orders
    created_a = order_factory(f'{generate_random_string()}-A', 3)
    created_b = order_factory(f'{generate_random_string()}-B', 7)

    # When: Listing with a large limit so everything fits in one page
    response = call_list_orders(limit=100)

    # Then: Both orders are returned
    assert response['statusCode'] == HTTPStatus.OK
    body = json.loads(response['body'])
    ids = {o['id'] for o in body['orders']}
    assert created_a['id'] in ids
    assert created_b['id'] in ids


def test_handler_pagination_walks_all_pages(order_factory):
    # Given: Three existing orders
    created_ids = {order_factory(f'{generate_random_string()}-X', i + 1)['id'] for i in range(3)}

    # When: Paginating through with limit=1
    seen: set[str] = set()
    token: str | None = None
    pages = 0
    while True:
        response = call_list_orders(limit=1, next_token=token)
        assert response['statusCode'] == HTTPStatus.OK
        body = json.loads(response['body'])
        seen.update(o['id'] for o in body['orders'])
        pages += 1
        token = body.get('next_token')
        if not token:
            break
        assert pages < 50  # safety: fail loudly if pagination never terminates

    # Then: Every created order surfaces, and we needed more than one page
    assert created_ids.issubset(seen)
    assert pages >= 2


def test_handler_invalid_next_token():
    # Given: A malformed next_token
    # When: The list handler is called with it
    response = call_list_orders(limit=10, next_token='not-valid-base64!!!')

    # Then: The response is a 400 Bad Request
    assert response['statusCode'] == HTTPStatus.BAD_REQUEST
    body = json.loads(response['body'])
    assert body == {'error': 'invalid next_token'}


def test_internal_server_error(mocker, table_name: str):
    # Given: A simulated error during DB interaction — patch pydynox client's sync_scan so the DAL try/except wraps it
    from pydynox import DynamoDBClient

    mocker.patch.object(DynamoDBClient, 'sync_scan', side_effect=Exception('DynamoDB error'))

    # When: The list orders lambda_handler is called
    response = call_list_orders(limit=10)

    # Then: The response reflects an internal server error
    assert response['statusCode'] == HTTPStatus.INTERNAL_SERVER_ERROR
    body = json.loads(response['body'])
    assert body == {'error': 'internal server error'}
