import os
from typing import Any, Dict, Literal
from unittest import mock

import pytest
from pydantic import BaseModel, HttpUrl

from cdk.aws_lambda_handler_cookbook.service_stack.constants import POWER_TOOLS_LOG_LEVEL, POWERTOOLS_SERVICE_NAME, SERVICE_NAME
from service.handlers.utils.env_vars_parser import get_environment_variables, init_environment_variables
from tests.utils import generate_context


class MySchema(BaseModel):
    POWERTOOLS_SERVICE_NAME: str
    LOG_LEVEL: Literal['DEBUG', 'INFO', 'ERROR', 'CRITICAL', 'WARNING', 'EXCEPTION']
    REST_API: HttpUrl


def test_handler_missing_env_var():

    @init_environment_variables(model=MySchema)
    def my_handler1(event, context) -> Dict[str, Any]:
        return {}

    with pytest.raises(ValueError):
        my_handler1({}, generate_context())


@mock.patch.dict(os.environ, {POWERTOOLS_SERVICE_NAME: SERVICE_NAME, POWER_TOOLS_LOG_LEVEL: 'DEBUG', 'REST_API': 'fakeapi'})
def test_handler_invalid_env_var_value():

    @init_environment_variables(model=MySchema)
    def my_handler2(event, context) -> Dict[str, Any]:
        return {}

    with pytest.raises(ValueError):
        my_handler2({}, generate_context())


@mock.patch.dict(os.environ, {
    POWERTOOLS_SERVICE_NAME: SERVICE_NAME,
    POWER_TOOLS_LOG_LEVEL: 'DEBUG',
    'REST_API': 'https://www.ranthebuilder.cloud/api'
})
def test_handler_schema_ok():

    @init_environment_variables(model=MySchema)
    def my_handler(event, context) -> Dict[str, Any]:
        env_vars: MySchema = get_environment_variables(model=MySchema)
        assert env_vars.POWERTOOLS_SERVICE_NAME == SERVICE_NAME
        assert env_vars.LOG_LEVEL == 'DEBUG'
        assert str(env_vars.REST_API) == 'https://www.ranthebuilder.cloud/api'
        return {}

    my_handler({}, generate_context())
