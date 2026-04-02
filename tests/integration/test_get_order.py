import json
from http import HTTPStatus

from service.dal.dynamo_dal_handler import DynamoDalHandler
from tests.integration.conftest import create_order_in_db
from tests.utils import generate_api_gw_event_with_path_params, generate_context, generate_random_string


def call_get_order(order_id: str) -> dict:
    from service.handlers.handle_get_order import lambda_handler

    event = generate_api_gw_event_with_path_params(
        http_method='GET',
        path=f'/api/orders/{order_id}',
        path_parameters={'order_id': order_id},
    )
    return lambda_handler(event, generate_context())


def test_handler_200_ok(table_name: str):
    # Given: An existing order in the database
    customer_name = f'{generate_random_string()}-RanTheBuilder'
    order_item_count = 5
    created_order = create_order_in_db(table_name, customer_name, order_item_count)

    # When: The get order lambda_handler is called with the order ID
    response = call_get_order(created_order['id'])

    # Then: Validate the response contains the correct order data
    assert response['statusCode'] == HTTPStatus.OK
    body_dict = json.loads(response['body'])
    assert body_dict['id'] == created_order['id']
    assert body_dict['name'] == customer_name
    assert body_dict['item_count'] == order_item_count


def test_handler_order_not_found():
    # Given: A non-existent order ID
    non_existent_id = '00000000-0000-0000-0000-000000000000'

    # When: The get order lambda_handler is called
    response = call_get_order(non_existent_id)

    # Then: Validate the response is a 404 not found
    assert response['statusCode'] == HTTPStatus.NOT_FOUND
    body_dict = json.loads(response['body'])
    assert body_dict == {'error': 'order was not found'}


def test_internal_server_error(mocker, table_name: str):
    # Given: A simulated error during DB interaction
    mocker.patch.object(DynamoDalHandler, '_get_order_model', side_effect=Exception('DynamoDB error'))

    # When: The get order lambda_handler is called
    response = call_get_order('00000000-0000-0000-0000-000000000001')

    # Then: Ensure the response reflects an internal server error
    assert response['statusCode'] == HTTPStatus.INTERNAL_SERVER_ERROR
    body_dict = json.loads(response['body'])
    assert body_dict == {'error': 'internal server error'}
