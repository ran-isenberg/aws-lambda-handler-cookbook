import os
from typing import Any

import pytest
from pydantic import BaseModel

from cdk.service.constants import CONFIGURATION_NAME, ENVIRONMENT, SERVICE_NAME
from service.handlers.utils.dynamic_configuration import parse_configuration
from service.models.exceptions import DynamicConfigurationException

MOCKED_SCHEMA = {'region': 'us-east-1'}


class MockedSchemaModel(BaseModel):
    region: str


def mock_dynamic_configuration(mocker, mock_schema: dict[str, Any]) -> None:
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
    # Given: Mocked dynamic configuration with an empty schema
    mock_dynamic_configuration(mocker, {})

    # When and Then: Parsing this configuration with our model, it should raise a DynamicConfigurationException
    with pytest.raises(DynamicConfigurationException):
        parse_configuration(model=MockedSchemaModel)


def test_valid_schema(mocker):
    # Given: Mocked dynamic configuration with a valid schema
    mock_dynamic_configuration(mocker, MOCKED_SCHEMA)

    # When and Then: Parsing this configuration with our model, it should not raise any exception
    parse_configuration(model=MockedSchemaModel)
