import json
from http import HTTPStatus
from typing import Any

from cdk.service.constants import READ_SCOPE, WRITE_SCOPE
from service.models.input import CreateOrderRequest
from tests.auth_utils import bearer_headers
from tests.utils import generate_api_gw_event, generate_api_gw_event_with_path_params, generate_context, generate_random_string

NON_EXISTENT_ID = '00000000-0000-0000-0000-000000000000'


def call_create_order(headers: dict[str, str] | None) -> dict[str, Any]:
    from service.handlers.handle_create_order import lambda_handler

    body = CreateOrderRequest(customer_name=f'{generate_random_string()}-RanTheBuilder', order_item_count=5)
    return lambda_handler(generate_api_gw_event(body.model_dump(), headers), generate_context())


def call_get_order(headers: dict[str, str] | None) -> dict[str, Any]:
    from service.handlers.handle_get_order import lambda_handler

    event = generate_api_gw_event_with_path_params(
        http_method='GET', path=f'/api/orders/{NON_EXISTENT_ID}', path_parameters={'order_id': NON_EXISTENT_ID}, headers=headers
    )
    return lambda_handler(event, generate_context())


def call_delete_order(headers: dict[str, str] | None) -> dict[str, Any]:
    from service.handlers.handle_delete_order import lambda_handler

    event = generate_api_gw_event_with_path_params(
        http_method='DELETE', path=f'/api/orders/{NON_EXISTENT_ID}', path_parameters={'order_id': NON_EXISTENT_ID}, headers=headers
    )
    return lambda_handler(event, generate_context())


def call_list_orders(headers: dict[str, str] | None) -> dict[str, Any]:
    from service.handlers.handle_list_orders import lambda_handler

    event = generate_api_gw_event_with_path_params(http_method='GET', path='/api/orders', path_parameters=None, headers=headers)
    event['queryStringParameters'] = None
    event['multiValueQueryStringParameters'] = None
    return lambda_handler(event, generate_context())


ALL_CALLS = [call_create_order, call_get_order, call_delete_order, call_list_orders]


def test_access_token_has_audience_and_scopes_of_the_groups(cognito_pool, writer_user, reader_user):
    # Given: A real writer and a real reader user, signed in with the Cognito API (their access tokens come from Cognito)
    from service.handlers.utils.auth import verifier

    # When: Verifying their access tokens with the same JWTVerifier the handlers use
    writer_claims = verifier.verify(writer_user.access_token)
    reader_claims = verifier.verify(reader_user.access_token)

    # Then: The pre token generation trigger added the audience and the scopes of the groups
    assert writer_claims['aud'] == cognito_pool.client_id
    assert writer_claims['client_id'] == cognito_pool.client_id
    assert writer_claims['token_use'] == 'access'
    assert {READ_SCOPE, WRITE_SCOPE}.issubset(writer_claims['scope'].split(' '))
    assert READ_SCOPE in reader_claims['scope'].split(' ')
    assert WRITE_SCOPE not in reader_claims['scope'].split(' ')


def test_missing_token_is_401():
    for call in ALL_CALLS:
        # Given: A request without an Authorization header
        # When: Calling the handler
        response = call(None)

        # Then: Unauthorized, with a challenge for the client
        assert response['statusCode'] == HTTPStatus.UNAUTHORIZED, call.__name__
        assert json.loads(response['body']) == {'message': 'Unauthorized'}
        assert response['multiValueHeaders']['WWW-Authenticate'] == ['Bearer']


def test_invalid_token_is_401():
    for call in ALL_CALLS:
        # Given: A request with a token that is not a JWT
        # When: Calling the handler
        response = call(bearer_headers('not-a-jwt'))

        # Then: Unauthorized
        assert response['statusCode'] == HTTPStatus.UNAUTHORIZED, call.__name__


def test_id_token_is_401(writer_user):
    for call in ALL_CALLS:
        # Given: A request with a real, valid Cognito ID token (not an access token)
        # When: Calling the handler
        response = call(bearer_headers(writer_user.id_token))

        # Then: Unauthorized, only access tokens are accepted
        assert response['statusCode'] == HTTPStatus.UNAUTHORIZED, call.__name__


def test_user_without_scope_is_403(no_scope_headers):
    # Given: A real user that is not a member of any group, so its access token has no orders scope
    for call in ALL_CALLS:
        # When: Calling the handler with its valid access token
        response = call(no_scope_headers)

        # Then: Forbidden (authenticated, but not authorized)
        assert response['statusCode'] == HTTPStatus.FORBIDDEN, call.__name__
        assert json.loads(response['body']) == {'message': 'Forbidden'}


def test_reader_cannot_write_but_can_read(reader_headers):
    # Given: A real reader (orders/read scope only)
    # When & Then: Write operations are forbidden
    assert call_create_order(reader_headers)['statusCode'] == HTTPStatus.FORBIDDEN
    assert call_delete_order(reader_headers)['statusCode'] == HTTPStatus.FORBIDDEN

    # When & Then: Read operations pass authorization (the order does not exist, so get is 404, list is 200)
    assert call_get_order(reader_headers)['statusCode'] == HTTPStatus.NOT_FOUND
    assert call_list_orders(reader_headers)['statusCode'] == HTTPStatus.OK


def test_writer_passes_authorization_on_every_route(writer_headers):
    # Given: A real writer (orders/read and orders/write scopes)
    # When & Then: Read and delete pass authorization (the order does not exist, so get and delete are 404, list is 200).
    # Creating an order as a writer is covered by test_create_order.py
    assert call_list_orders(writer_headers)['statusCode'] == HTTPStatus.OK
    assert call_get_order(writer_headers)['statusCode'] == HTTPStatus.NOT_FOUND
    assert call_delete_order(writer_headers)['statusCode'] == HTTPStatus.NOT_FOUND
