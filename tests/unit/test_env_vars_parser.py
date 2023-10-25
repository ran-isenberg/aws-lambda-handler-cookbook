import os
from typing import Any, Literal
from unittest import mock

import pytest
from aws_lambda_env_modeler import get_environment_variables, init_environment_variables
from pydantic import BaseModel, HttpUrl

from cdk.service.constants import POWER_TOOLS_LOG_LEVEL, POWERTOOLS_SERVICE_NAME, SERVICE_NAME
from tests.utils import generate_context


class MySchema(BaseModel):
    POWERTOOLS_SERVICE_NAME: str
    LOG_LEVEL: Literal['DEBUG', 'INFO', 'ERROR', 'CRITICAL', 'WARNING', 'EXCEPTION']
    REST_API: HttpUrl


def test_handler_missing_env_var():
    # Given: A handler that requires certain environment variables
    @init_environment_variables(model=MySchema)
    def my_handler1(event, context) -> dict[str, Any]:
        return {}

    # When & Then: Handler is invoked without the required environment variables, expect a ValueError
    with pytest.raises(ValueError):
        my_handler1({}, generate_context())


@mock.patch.dict(os.environ, {POWERTOOLS_SERVICE_NAME: SERVICE_NAME, POWER_TOOLS_LOG_LEVEL: 'DEBUG', 'REST_API': 'fakeapi'})
def test_handler_invalid_env_var_value():
    # Given: A handler that requires certain environment variables with valid values
    @init_environment_variables(model=MySchema)
    def my_handler2(event, context) -> dict[str, Any]:
        return {}

    # When & Then: Handler is invoked with invalid environment variable values, expect a ValueError
    with pytest.raises(ValueError):
        my_handler2({}, generate_context())


@mock.patch.dict(
    os.environ, {POWERTOOLS_SERVICE_NAME: SERVICE_NAME, POWER_TOOLS_LOG_LEVEL: 'DEBUG', 'REST_API': 'https://www.ranthebuilder.cloud/api'}
)
def test_handler_schema_ok():
    # Given: A handler that requires certain environment variables with valid values
    @init_environment_variables(model=MySchema)
    def my_handler(event, context) -> dict[str, Any]:
        # When: Environment variables are retrieved
        env_vars: MySchema = get_environment_variables(model=MySchema)

        # Then: Retrieved variables should match expected values
        assert env_vars.POWERTOOLS_SERVICE_NAME == SERVICE_NAME
        assert env_vars.LOG_LEVEL == 'DEBUG'
        assert str(env_vars.REST_API) == 'https://www.ranthebuilder.cloud/api'
        return {}

    # No exception should be raised
    my_handler({}, generate_context())
