import pytest
from pydantic import ValidationError

from service.handlers.models.env_vars import DeleteHandlerEnvVars, GetHandlerEnvVars, ListHandlerEnvVars

VALID_BASE = {
    'POWERTOOLS_SERVICE_NAME': 'Orders',
    'LOG_LEVEL': 'INFO',
    'TABLE_NAME': 'orders-table',
    'COGNITO_USER_POOL_ID': 'us-east-1_AbC123xyz',
    'COGNITO_CLIENT_ID': '1example23456789',
}


@pytest.mark.parametrize('model', [GetHandlerEnvVars, DeleteHandlerEnvVars, ListHandlerEnvVars])
def test_valid(model):
    # Given: A valid set of environment variables
    # When: The env vars model is constructed
    env = model(**VALID_BASE)

    # Then: The values are preserved
    assert env.POWERTOOLS_SERVICE_NAME == 'Orders'
    assert env.LOG_LEVEL == 'INFO'
    assert env.TABLE_NAME == 'orders-table'
    assert env.COGNITO_USER_POOL_ID == 'us-east-1_AbC123xyz'
    assert env.COGNITO_CLIENT_ID == '1example23456789'


@pytest.mark.parametrize('model', [GetHandlerEnvVars, DeleteHandlerEnvVars, ListHandlerEnvVars])
def test_missing_table_name(model):
    # Given: A payload without TABLE_NAME
    payload = {k: v for k, v in VALID_BASE.items() if k != 'TABLE_NAME'}

    # When & Then: Construction fails with a ValidationError
    with pytest.raises(ValidationError):
        model(**payload)


@pytest.mark.parametrize('model', [GetHandlerEnvVars, DeleteHandlerEnvVars, ListHandlerEnvVars])
def test_empty_table_name(model):
    # Given: An empty TABLE_NAME
    payload = {**VALID_BASE, 'TABLE_NAME': ''}

    # When & Then: Construction fails due to min_length=1
    with pytest.raises(ValidationError):
        model(**payload)


@pytest.mark.parametrize('model', [GetHandlerEnvVars, DeleteHandlerEnvVars, ListHandlerEnvVars])
def test_invalid_log_level(model):
    # Given: A LOG_LEVEL value outside the allowed Literal set
    payload = {**VALID_BASE, 'LOG_LEVEL': 'VERBOSE'}

    # When & Then: Construction fails
    with pytest.raises(ValidationError):
        model(**payload)


@pytest.mark.parametrize('model', [GetHandlerEnvVars, DeleteHandlerEnvVars, ListHandlerEnvVars])
@pytest.mark.parametrize('missing', ['COGNITO_USER_POOL_ID', 'COGNITO_CLIENT_ID'])
def test_missing_cognito_vars(model, missing):
    # Given: A payload without one of the Cognito variables
    payload = {k: v for k, v in VALID_BASE.items() if k != missing}

    # When & Then: Construction fails with a ValidationError
    with pytest.raises(ValidationError):
        model(**payload)


@pytest.mark.parametrize('model', [GetHandlerEnvVars, DeleteHandlerEnvVars, ListHandlerEnvVars])
@pytest.mark.parametrize('pool_id', ['', 'no-underscore', 'us-east-1', 'US-EAST-1_abc', 'us-east-1_'])
def test_invalid_user_pool_id(model, pool_id):
    # Given: A malformed user pool id
    payload = {**VALID_BASE, 'COGNITO_USER_POOL_ID': pool_id}

    # When & Then: Construction fails, before the JWTVerifier is built with it
    with pytest.raises(ValidationError):
        model(**payload)


@pytest.mark.parametrize('model', [GetHandlerEnvVars, DeleteHandlerEnvVars, ListHandlerEnvVars])
def test_cognito_jwks_is_optional(model):
    # Given: A payload without COGNITO_JWKS (functions that download the JWKS at runtime)
    # When: The env vars model is constructed
    env = model(**VALID_BASE)

    # Then: The verifier gets no pre-fetched keys
    assert env.COGNITO_JWKS is None


def test_cognito_jwks_is_parsed():
    # Given: A JWKS JSON string, as the CDK custom resource sets it
    payload = {**VALID_BASE, 'COGNITO_JWKS': '{"keys":[{"kid":"abc","kty":"RSA"}]}'}

    # When: The env vars model is constructed
    env = ListHandlerEnvVars(**payload)

    # Then: The JWKS is parsed into a dict the verifier accepts
    assert env.COGNITO_JWKS == {'keys': [{'kid': 'abc', 'kty': 'RSA'}]}


def test_cognito_jwks_invalid_json():
    # Given: A COGNITO_JWKS value that is not JSON
    payload = {**VALID_BASE, 'COGNITO_JWKS': 'not-json'}

    # When & Then: Construction fails
    with pytest.raises(ValidationError):
        ListHandlerEnvVars(**payload)
