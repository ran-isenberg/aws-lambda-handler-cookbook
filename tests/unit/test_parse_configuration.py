import os
from typing import Any, Dict

import pytest
from aws_lambda_powertools.utilities.feature_flags.exceptions import SchemaValidationError
from pydantic import BaseModel

from cdk.my_service.constants import CONFIGURATION_NAME, ENVIRONMENT, SERVICE_NAME
from service.handlers.utils.dynamic_configuration import parse_configuration

MOCKED_SCHEMA = {'region': 'us-east-1'}


class MockedSchemaModel(BaseModel):
    region: str


def mock_dynamic_configuration(mocker, mock_schema: Dict[str, Any]) -> None:
    """Mock AppConfig Store get_configuration method to use mock schema instead"""
    mocked_get_conf = mocker.patch('aws_lambda_powertools.utilities.parameters.AppConfigProvider.get')
    mocked_get_conf.return_value = mock_schema


@pytest.fixture(scope='module', autouse=True)
def init():
    os.environ['CONFIGURATION_APP'] = SERVICE_NAME
    os.environ['CONFIGURATION_ENV'] = ENVIRONMENT
    os.environ['CONFIGURATION_NAME'] = CONFIGURATION_NAME
    os.environ['CONFIGURATION_MAX_AGE_MINUTES'] = '5'


def test_invalid_schema(mocker):
    mock_dynamic_configuration(mocker, {})
    with pytest.raises(SchemaValidationError):
        parse_configuration(model=MockedSchemaModel)


def test_valid_schema(mocker):
    mock_dynamic_configuration(mocker, MOCKED_SCHEMA)
    parse_configuration(model=MockedSchemaModel)
