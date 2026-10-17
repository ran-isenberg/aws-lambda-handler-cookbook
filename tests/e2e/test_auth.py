import json
from http import HTTPStatus

import pytest
import requests

from cdk.service.constants import SWAGGER_URL
from service.models.input import CreateOrderRequest
from tests.auth_utils import bearer_headers
from tests.utils import generate_random_string, get_stack_output

NON_EXISTENT_ID = '00000000-0000-0000-0000-000000000000'


def call_api(api_gw_url: str, method: str, headers: dict[str, str] | None) -> requests.Response:
    """Call one of the four protected order routes (create, get, delete, list) over HTTP."""
    if method == 'POST':
        body = CreateOrderRequest(customer_name=f'{generate_random_string()}-RanTheBuilder', order_item_count=5)
        return requests.post(api_gw_url, data=body.model_dump_json(), headers=headers)
    if method == 'GET_ONE':
        return requests.get(f'{api_gw_url}/{NON_EXISTENT_ID}', headers=headers)
    if method == 'DELETE':
        return requests.delete(f'{api_gw_url}/{NON_EXISTENT_ID}', headers=headers)
    return requests.get(api_gw_url, headers=headers)


ALL_ROUTES = ['POST', 'GET_ONE', 'DELETE', 'LIST']


@pytest.mark.parametrize('route', ALL_ROUTES)
def test_missing_token_is_401(api_gw_url, route):
    # Given: A request without an Authorization header
    # When: Calling a protected route
    response = call_api(api_gw_url, route, None)

    # Then: Unauthorized, with a challenge for the client
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert json.loads(response.text) == {'message': 'Unauthorized'}
    # API Gateway remaps the WWW-Authenticate header of the Lambda response
    assert response.headers['x-amzn-Remapped-WWW-Authenticate'] == 'Bearer'


@pytest.mark.parametrize('route', ALL_ROUTES)
def test_invalid_token_is_401(api_gw_url, route):
    # Given: A token that is not a JWT
    # When: Calling a protected route
    response = call_api(api_gw_url, route, bearer_headers('not-a-jwt'))

    # Then: Unauthorized
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.parametrize('route', ALL_ROUTES)
def test_id_token_is_401(api_gw_url, manager_user, route):
    # Given: A real, valid Cognito ID token (not an access token)
    # When: Calling a protected route
    response = call_api(api_gw_url, route, bearer_headers(manager_user.id_token))

    # Then: Unauthorized, only access tokens are accepted
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_member_can_create_but_not_delete(api_gw_url, member_user, member_headers, tracked_orders):
    # Given: A real signed in user in no group, so its access token has no orders/manage scope
    # When: Creating an order
    response = call_api(api_gw_url, 'POST', member_headers)

    # Then: The order is created and the member can get it, but deleting it is forbidden (authenticated, but not authorized)
    assert response.status_code == HTTPStatus.OK
    order_id = json.loads(response.text)['id']
    tracked_orders.append((member_user.sub, order_id))
    assert requests.get(f'{api_gw_url}/{order_id}', headers=member_headers).status_code == HTTPStatus.OK
    deleted = requests.delete(f'{api_gw_url}/{order_id}', headers=member_headers)
    assert deleted.status_code == HTTPStatus.FORBIDDEN
    assert json.loads(deleted.text) == {'message': 'Forbidden'}


def test_member_can_get_and_list_own_orders(api_gw_url, order_factory, member_user, member_headers):
    # Given: An order of a signed in user in no group (created for it directly in the table)
    order = order_factory(member_user, f'{generate_random_string()}-Member', 2)

    # When & Then: Getting and listing only need a valid access token, no scope
    assert requests.get(f'{api_gw_url}/{order["id"]}', headers=member_headers).status_code == HTTPStatus.OK
    listed = requests.get(api_gw_url, params={'limit': 100}, headers=member_headers)
    assert listed.status_code == HTTPStatus.OK
    assert order['id'] in {o['id'] for o in json.loads(listed.text)['orders']}


def test_manager_can_delete(api_gw_url, manager_user, manager_headers, tracked_orders):
    # Given: A real manager (orders/manage scope) and an order it created
    response = call_api(api_gw_url, 'POST', manager_headers)

    # When & Then: The manager can get and delete its own order
    assert response.status_code == HTTPStatus.OK
    order_id = json.loads(response.text)['id']
    tracked_orders.append((manager_user.sub, order_id))
    assert requests.get(f'{api_gw_url}/{order_id}', headers=manager_headers).status_code == HTTPStatus.OK
    assert requests.delete(f'{api_gw_url}/{order_id}', headers=manager_headers).status_code == HTTPStatus.OK


def test_swagger_is_public():
    # Given: The swagger endpoint
    # When: Calling it without a token
    response = requests.get(get_stack_output(SWAGGER_URL))

    # Then: It is still reachable
    assert response.status_code == HTTPStatus.OK
