import json
from http import HTTPStatus
from typing import Any

from cdk.service.constants import MANAGE_SCOPE
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


def test_access_token_has_audience_and_scopes_of_the_groups(cognito_pool, manager_user, member_user):
    # Given: A real manager and a real member (no group), signed in with the Cognito API (their access tokens come from Cognito)
    from service.handlers.utils.auth import verifier

    # When: Verifying their access tokens with the same JWTVerifier the handlers use
    manager_claims = verifier.verify(manager_user.access_token)
    member_claims = verifier.verify(member_user.access_token)

    # Then: The pre token generation trigger added the audience to both, and the manage scope only to the manager
    for claims in (manager_claims, member_claims):
        assert claims['aud'] == cognito_pool.client_id
        assert claims['client_id'] == cognito_pool.client_id
        assert claims['token_use'] == 'access'
    assert MANAGE_SCOPE in manager_claims['scope'].split(' ')
    assert MANAGE_SCOPE not in member_claims.get('scope', '').split(' ')


def test_missing_token_is_401():
    for call in ALL_CALLS:
        # Given: A request without an Authorization header
        # When: Calling the handler
        response = call(None)

        # Then: Unauthorized, with a challenge for the client
        assert response['statusCode'] == HTTPStatus.UNAUTHORIZED, call.__name__
        assert json.loads(response['body']) == {'message': 'Unauthorized'}
        assert response['multiValueHeaders']['WWW-Authenticate'] == ['Bearer']


def test_request_validation_runs_before_authorization():
    # Given: Invalid requests without an Authorization header (an invalid body, and a limit outside 1-100)
    from service.handlers.handle_create_order import lambda_handler as create_handler
    from service.handlers.handle_list_orders import lambda_handler as list_handler

    create_event = generate_api_gw_event({'customer_name': 'RanTheBuilder', 'order_item_count': 'not-a-number'}, None)
    list_event = generate_api_gw_event_with_path_params(http_method='GET', path='/api/orders', path_parameters=None, headers=None)
    list_event['queryStringParameters'] = {'limit': '0'}
    list_event['multiValueQueryStringParameters'] = {'limit': ['0']}

    # When: Calling the handlers
    create_response = create_handler(create_event, generate_context())
    list_response = list_handler(list_event, generate_context())

    # Then: The Event Handler validates the request before the auth middleware runs, so it is 422 and not 401
    # (documented in docs/best_practices/authentication.md, a Powertools upgrade that changes the order fails this test)
    assert create_response['statusCode'] == HTTPStatus.UNPROCESSABLE_ENTITY
    assert list_response['statusCode'] == HTTPStatus.UNPROCESSABLE_ENTITY


def test_invalid_token_is_401():
    for call in ALL_CALLS:
        # Given: A request with a token that is not a JWT
        # When: Calling the handler
        response = call(bearer_headers('not-a-jwt'))

        # Then: Unauthorized
        assert response['statusCode'] == HTTPStatus.UNAUTHORIZED, call.__name__


def test_id_token_is_401(manager_user):
    for call in ALL_CALLS:
        # Given: A request with a real, valid Cognito ID token (not an access token)
        # When: Calling the handler
        response = call(bearer_headers(manager_user.id_token))

        # Then: Unauthorized, only access tokens are accepted
        assert response['statusCode'] == HTTPStatus.UNAUTHORIZED, call.__name__


def test_member_cannot_delete(member_headers):
    # Given: A real signed in user in no group, so its access token has no orders/manage scope
    # When: Deleting an order with its valid access token
    response = call_delete_order(member_headers)

    # Then: Forbidden (authenticated, but not authorized). Creating orders is covered by test_create_order.py
    assert response['statusCode'] == HTTPStatus.FORBIDDEN
    assert json.loads(response['body']) == {'message': 'Forbidden'}


def test_member_can_get_and_list_own_orders(order_factory, member_user, member_headers):
    # Given: An order of a signed in user in no group (orders are created for it directly in the table)
    from tests.integration.test_get_order import call_get_order as call_get_order_by_id
    from tests.integration.test_list_orders import call_list_orders as call_list_orders_with_limit

    order = order_factory(member_user, f'{generate_random_string()}-Member', 2)

    # When & Then: Getting and listing only need a valid access token, no scope
    assert call_get_order_by_id(order['id'], member_headers)['statusCode'] == HTTPStatus.OK
    listed = call_list_orders_with_limit(member_headers, limit=100)
    assert listed['statusCode'] == HTTPStatus.OK
    assert order['id'] in {o['id'] for o in json.loads(listed['body'])['orders']}


def test_manager_passes_authorization_on_every_route(manager_headers):
    # Given: A real manager (orders/manage scope)
    # When & Then: Every route passes authorization (the order does not exist, so get and delete are 404, list is 200).
    # Deleting an existing order as a manager is covered by test_delete_order.py
    assert call_list_orders(manager_headers)['statusCode'] == HTTPStatus.OK
    assert call_get_order(manager_headers)['statusCode'] == HTTPStatus.NOT_FOUND
    assert call_delete_order(manager_headers)['statusCode'] == HTTPStatus.NOT_FOUND
