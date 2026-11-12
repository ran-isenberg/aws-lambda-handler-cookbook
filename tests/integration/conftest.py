import os
import uuid
from collections.abc import Iterator
from dataclasses import dataclass
from urllib.parse import urlparse

import boto3
import pytest

from cdk.service.constants import (
    CONFIGURATION_NAME,
    ENVIRONMENT,
    MANAGERS_GROUP,
    POWER_TOOLS_LOG_LEVEL,
    POWERTOOLS_SERVICE_NAME,
    SERVICE_NAME,
)
from tests.auth_utils import CognitoPool, CognitoUser
from tests.integration.tokens import TokenIssuer

# The integration tests run against a local AWS Emulator (make emulator-start), never against a real AWS account.
# The Makefile sets the emulator env (AWS_ENDPOINT_URL, its credentials and CA) before pytest starts, because
# DynamoDB clients are created at import time (tests/conftest.py).
EMULATOR_HOSTS = {'127.0.0.1', 'localhost'}


def pytest_sessionstart(session: pytest.Session) -> None:
    endpoint = os.environ.get('AWS_ENDPOINT_URL', '')
    if urlparse(endpoint).hostname not in EMULATOR_HOSTS:
        pytest.exit(
            f'integration tests run only against a local AWS Emulator, AWS_ENDPOINT_URL is {endpoint!r}. '
            'Run them with `make integration` or `make coverage-tests` after `make emulator-start`.',
            returncode=1,
        )


@dataclass(frozen=True)
class EmulatorResources:
    table_name: str
    idempotency_table_name: str


def _create_table(client, name: str, key_names: list[str]) -> None:
    """key_names: the partition key, then the optional sort key (all strings)."""
    key_types = ['HASH', 'RANGE'][: len(key_names)]
    client.create_table(
        TableName=name,
        AttributeDefinitions=[{'AttributeName': key, 'AttributeType': 'S'} for key in key_names],
        KeySchema=[{'AttributeName': key, 'KeyType': key_type} for key, key_type in zip(key_names, key_types, strict=True)],
        BillingMode='PAY_PER_REQUEST',
    )
    client.get_waiter('table_exists').wait(TableName=name, WaiterConfig={'Delay': 1, 'MaxAttempts': 30})


@pytest.fixture(scope='session')
def emulator_resources() -> Iterator[EmulatorResources]:
    """The two DynamoDB tables of cdk/service/api_db_construct.py, with unique names per test session.

    Deletion is asynchronous (as on AWS), so a name can't be reused right after DeleteTable.
    """
    client = boto3.client('dynamodb')
    suffix = uuid.uuid4().hex[:8]
    resources = EmulatorResources(table_name=f'orders-{suffix}', idempotency_table_name=f'idempotency-{suffix}')
    _create_table(client, resources.table_name, ['owner_id', 'id'])
    _create_table(client, resources.idempotency_table_name, ['id'])
    yield resources
    for name in (resources.table_name, resources.idempotency_table_name):
        client.delete_table(TableName=name)


@pytest.fixture(scope='module')
def table_name(emulator_resources: EmulatorResources) -> str:
    return emulator_resources.table_name


# Tokens are minted locally and signed with a per session key (see tokens.py for why the emulator's Cognito isn't used).
@pytest.fixture(scope='session')
def token_issuer() -> TokenIssuer:
    return TokenIssuer()


@pytest.fixture(scope='session')
def cognito_pool(token_issuer: TokenIssuer) -> CognitoPool:
    return token_issuer.pool


@pytest.fixture(scope='session')
def manager_user(token_issuer: TokenIssuer) -> CognitoUser:
    return token_issuer.create_user([MANAGERS_GROUP])


@pytest.fixture(scope='session')
def other_manager_user(token_issuer: TokenIssuer) -> CognitoUser:
    return token_issuer.create_user([MANAGERS_GROUP])


@pytest.fixture(scope='session')
def member_user(token_issuer: TokenIssuer) -> CognitoUser:
    return token_issuer.create_user([])


@pytest.fixture(scope='module', autouse=True)
def init(table_name, emulator_resources, cognito_pool, token_issuer):
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
    os.environ['IDEMPOTENCY_TABLE_NAME'] = emulator_resources.idempotency_table_name
    # the handlers verify the locally minted access tokens with their real JWTVerifier, using the session's public key
    os.environ['COGNITO_USER_POOL_ID'] = cognito_pool.user_pool_id
    os.environ['COGNITO_CLIENT_ID'] = cognito_pool.client_id
    os.environ['COGNITO_JWKS'] = token_issuer.jwks()
