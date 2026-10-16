import io
import json
from unittest.mock import patch

import pytest

from service.handlers.handle_fetch_jwks import lambda_handler
from service.logic.jwks import fetch_jwks, jwks_url

USER_POOL_ID = 'us-east-1_AbC123xyz'
JWKS = {'keys': [{'kid': 'abc', 'kty': 'RSA', 'alg': 'RS256', 'use': 'sig', 'n': 'n', 'e': 'AQAB'}]}


def _mock_urlopen(body: object):
    return patch('service.logic.jwks.urllib.request.urlopen', return_value=io.BytesIO(json.dumps(body).encode()))


@pytest.mark.parametrize(
    'user_pool_id, expected',
    [
        (USER_POOL_ID, 'https://cognito-idp.us-east-1.amazonaws.com/us-east-1_AbC123xyz/.well-known/jwks.json'),
        ('cn-north-1_AbC123xyz', 'https://cognito-idp.cn-north-1.amazonaws.com.cn/cn-north-1_AbC123xyz/.well-known/jwks.json'),
    ],
)
def test_jwks_url(user_pool_id, expected):
    # Given: A user pool id
    # When & Then: The JWKS URL matches the one the Powertools JWTVerifier Cognito profile uses
    assert jwks_url(user_pool_id) == expected


def test_fetch_jwks():
    # Given: The Cognito JWKS endpoint returns a key set
    with _mock_urlopen(JWKS) as urlopen:
        # When: Fetching the JWKS
        jwks = fetch_jwks(USER_POOL_ID)

    # Then: The key set is returned as a JSON string, fetched from the user pool URL
    assert json.loads(jwks) == JWKS
    assert urlopen.call_args.args[0] == jwks_url(USER_POOL_ID)


@pytest.mark.parametrize('body', [{}, {'keys': []}, {'keys': 'nope'}, ['keys']])
def test_fetch_jwks_invalid_response(body):
    # Given: The endpoint returns something that is not a key set
    with _mock_urlopen(body):
        # When & Then: Fetching fails, so the deployment fails instead of shipping a Lambda that rejects every token
        with pytest.raises(ValueError):
            fetch_jwks(USER_POOL_ID)


@pytest.mark.parametrize('request_type', ['Create', 'Update'])
def test_custom_resource_create_update(request_type):
    # Given: A custom resource create/update event
    event = {'RequestType': request_type, 'ResourceProperties': {'UserPoolId': USER_POOL_ID}, 'PhysicalResourceId': 'old'}

    with _mock_urlopen(JWKS):
        # When: The handler runs
        response = lambda_handler(event, None)

    # Then: The JWKS is returned as the 'Jwks' attribute, keyed by the user pool id
    assert response['PhysicalResourceId'] == USER_POOL_ID
    assert json.loads(response['Data']['Jwks']) == JWKS


def test_custom_resource_delete():
    # Given: A custom resource delete event
    event = {'RequestType': 'Delete', 'ResourceProperties': {'UserPoolId': USER_POOL_ID}, 'PhysicalResourceId': USER_POOL_ID}

    with patch('service.logic.jwks.urllib.request.urlopen') as urlopen:
        # When: The handler runs
        response = lambda_handler(event, None)

    # Then: Nothing is fetched
    urlopen.assert_not_called()
    assert response == {'PhysicalResourceId': USER_POOL_ID}
