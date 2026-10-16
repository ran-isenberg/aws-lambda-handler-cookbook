import base64
import json
from collections.abc import Iterator
from typing import Any

import pytest

from service.dal.dynamo_dal_handler import DynamoDalHandler
from service.models.exceptions import InternalServerException, InvalidNextTokenException

OWNER_ID = 'owner-sub-1'
ORDER_ID = '7f1b8d2c-3a4e-4c5b-9d6e-1f2a3b4c5d6e'


def _token(start_key: Any) -> str:
    return base64.urlsafe_b64encode(json.dumps(start_key).encode()).decode()


@pytest.fixture
def resolver(monkeypatch) -> Iterator[Any]:
    # the auth module builds the JWTVerifier at import time from the Cognito environment variables (no network call)
    monkeypatch.setenv('COGNITO_USER_POOL_ID', 'us-east-1_AbC123xyz')
    monkeypatch.setenv('COGNITO_CLIENT_ID', '1example23456789')
    from service.handlers.utils.rest_api_resolver import app

    yield app
    app.clear_context()


def test_get_caller_id_is_the_sub_claim(resolver):
    from service.handlers.utils.auth import get_caller_id

    # Given: The verified claims that the auth middleware adds to the resolver context
    resolver.append_context(claims={'sub': OWNER_ID, 'username': 'reusable-name'})

    # When & Then: The caller id is the immutable sub claim, not the username
    assert get_caller_id() == OWNER_ID


@pytest.mark.parametrize('context', [{}, {'claims': {}}, {'claims': {'sub': ''}}, {'claims': {'sub': 7}}])
def test_get_caller_id_without_verified_sub(resolver, context):
    from service.handlers.utils.auth import get_caller_id

    # Given: No verified claims with a sub claim (a route without the auth middleware)
    resolver.append_context(**context)

    # When & Then: It fails closed (500) instead of using an empty or shared owner
    with pytest.raises(InternalServerException):
        get_caller_id()


def test_next_token_round_trip():
    # Given: The last evaluated key of the caller's query
    start_key = {'owner_id': OWNER_ID, 'id': ORDER_ID}

    # When: It is encoded as next_token and decoded by the same caller
    decoded = DynamoDalHandler._decode_next_token(DynamoDalHandler._encode_next_token(start_key), OWNER_ID)

    # Then: The query continues from the same key
    assert decoded == start_key


def test_no_next_token():
    # Given & When & Then: No next_token starts the query from the beginning
    assert DynamoDalHandler._decode_next_token(None, OWNER_ID) is None


@pytest.mark.parametrize(
    'next_token',
    [
        'not-valid-base64!!!',
        _token({'owner_id': 'another-user', 'id': ORDER_ID}),  # another user's next_token
        _token({'id': ORDER_ID}),  # no owner
        _token({'owner_id': OWNER_ID, 'id': ORDER_ID, 'extra': 'x'}),  # not a key of the table
        _token({'owner_id': OWNER_ID, 'id': 5}),
        _token([OWNER_ID, ORDER_ID]),
    ],
)
def test_invalid_next_token(next_token):
    # Given: A next_token that is malformed or does not belong to the caller
    # When & Then: It is rejected (400) before reaching DynamoDB
    with pytest.raises(InvalidNextTokenException):
        DynamoDalHandler._decode_next_token(next_token, OWNER_ID)
