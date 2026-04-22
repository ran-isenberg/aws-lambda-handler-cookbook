import pytest
from pydantic import ValidationError

from service.handlers.models.env_vars import DeleteHandlerEnvVars, GetHandlerEnvVars, ListHandlerEnvVars

VALID_BASE = {'POWERTOOLS_SERVICE_NAME': 'Orders', 'LOG_LEVEL': 'INFO', 'TABLE_NAME': 'orders-table'}


@pytest.mark.parametrize('model', [GetHandlerEnvVars, DeleteHandlerEnvVars, ListHandlerEnvVars])
def test_valid(model):
    # Given: A valid set of environment variables
    # When: The env vars model is constructed
    env = model(**VALID_BASE)

    # Then: The values are preserved
    assert env.POWERTOOLS_SERVICE_NAME == 'Orders'
    assert env.LOG_LEVEL == 'INFO'
    assert env.TABLE_NAME == 'orders-table'


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
