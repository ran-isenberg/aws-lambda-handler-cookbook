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
def test_id_token_is_401(api_gw_url, writer_user, route):
    # Given: A real, valid Cognito ID token (not an access token)
    # When: Calling a protected route
    response = call_api(api_gw_url, route, bearer_headers(writer_user.id_token))

    # Then: Unauthorized, only access tokens are accepted
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.parametrize('route', ALL_ROUTES)
def test_user_without_scope_is_403(api_gw_url, no_scope_headers, route):
    # Given: A real user that is not a member of any group, so its access token has no orders scope
    # When: Calling a protected route with its valid access token
    response = call_api(api_gw_url, route, no_scope_headers)

    # Then: Forbidden (authenticated, but not authorized)
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert json.loads(response.text) == {'message': 'Forbidden'}


@pytest.mark.parametrize('route', ['POST', 'DELETE'])
def test_reader_cannot_write(api_gw_url, reader_headers, route):
    # Given: A real reader (orders/read scope only)
    # When: Calling a write route
    response = call_api(api_gw_url, route, reader_headers)

    # Then: Forbidden
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_reader_can_read(api_gw_url, reader_headers):
    # Given: A real reader (orders/read scope only)
    # When & Then: Read routes pass authorization (the order does not exist, so get is 404, list is 200)
    assert call_api(api_gw_url, 'LIST', reader_headers).status_code == HTTPStatus.OK
    assert call_api(api_gw_url, 'GET_ONE', reader_headers).status_code == HTTPStatus.NOT_FOUND


def test_writer_can_read_and_write(api_gw_url, writer_headers, tracked_order_ids):
    # Given: A real writer (orders/read and orders/write scopes)
    # When: Creating an order
    response = call_api(api_gw_url, 'POST', writer_headers)

    # Then: The order is created and can be read and deleted
    assert response.status_code == HTTPStatus.OK
    order_id = json.loads(response.text)['id']
    tracked_order_ids.append(order_id)
    assert requests.get(f'{api_gw_url}/{order_id}', headers=writer_headers).status_code == HTTPStatus.OK
    assert requests.delete(f'{api_gw_url}/{order_id}', headers=writer_headers).status_code == HTTPStatus.OK


def test_swagger_is_public():
    # Given: The swagger endpoint
    # When: Calling it without a token
    response = requests.get(get_stack_output(SWAGGER_URL))

    # Then: It is still reachable
    assert response.status_code == HTTPStatus.OK
