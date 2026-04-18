import os

import pytest

from cdk.service.constants import (
    CONFIGURATION_NAME,
    ENVIRONMENT,
    IDEMPOTENCY_TABLE_NAME_OUTPUT,
    POWER_TOOLS_LOG_LEVEL,
    POWERTOOLS_SERVICE_NAME,
    SERVICE_NAME,
)
from tests.utils import get_stack_output


@pytest.fixture(scope='module', autouse=True)
def init(table_name):
    os.environ[POWERTOOLS_SERVICE_NAME] = SERVICE_NAME
    os.environ[POWER_TOOLS_LOG_LEVEL] = 'DEBUG'
    os.environ['REST_API'] = 'https://www.ranthebuilder.cloud/api'
    os.environ['ROLE_ARN'] = 'arn:partition:service:region:account-id:resource-type:resource-id'
    os.environ['CONFIGURATION_APP'] = SERVICE_NAME
    os.environ['CONFIGURATION_ENV'] = ENVIRONMENT
    os.environ['CONFIGURATION_NAME'] = CONFIGURATION_NAME
    os.environ['CONFIGURATION_MAX_AGE_MINUTES'] = '5'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'  # used for appconfig mocked boto calls
    os.environ['TABLE_NAME'] = table_name
    os.environ['IDEMPOTENCY_TABLE_NAME'] = get_stack_output(IDEMPOTENCY_TABLE_NAME_OUTPUT)
