import os
import uuid
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any

import pytest
from pydynox import DynamoDBClient, dynamodb_model

from cdk.service.constants import (
    CONFIGURATION_NAME,
    ENVIRONMENT,
    IDEMPOTENCY_TABLE_NAME_OUTPUT,
    POWER_TOOLS_LOG_LEVEL,
    POWERTOOLS_SERVICE_NAME,
    SERVICE_NAME,
    TABLE_NAME_OUTPUT,
)
from service.dal.models.db import OrderEntry
from tests.utils import get_stack_output

_dynamo_client = DynamoDBClient()


@lru_cache
def _get_order_model(table_name: str):
    @dynamodb_model(table=table_name, partition_key='id', client=_dynamo_client)
    class DynamoOrderEntry(OrderEntry):
        pass

    return DynamoOrderEntry


def create_order_in_db(table_name: str, customer_name: str, order_item_count: int) -> dict[str, Any]:
    """Create an order directly in DynamoDB via pydynox."""
    order_id = str(uuid.uuid4())
    entry = _get_order_model(table_name)(
        id=order_id,
        name=customer_name,
        item_count=order_item_count,
        created_at=int(datetime.now(timezone.utc).timestamp()),
    )
    entry.sync_save()
    return {'id': order_id, 'name': customer_name, 'item_count': order_item_count}


def get_order_from_db(table_name: str, order_id: str) -> OrderEntry | None:
    """Get an order directly from DynamoDB via pydynox. Returns None if not found."""
    return _get_order_model(table_name).sync_get(id=order_id)


@pytest.fixture(scope='module', autouse=True)
def init():
    os.environ[POWERTOOLS_SERVICE_NAME] = SERVICE_NAME
    os.environ[POWER_TOOLS_LOG_LEVEL] = 'DEBUG'
    os.environ['REST_API'] = 'https://www.ranthebuilder.cloud/api'
    os.environ['ROLE_ARN'] = 'arn:partition:service:region:account-id:resource-type:resource-id'
    os.environ['CONFIGURATION_APP'] = SERVICE_NAME
    os.environ['CONFIGURATION_ENV'] = ENVIRONMENT
    os.environ['CONFIGURATION_NAME'] = CONFIGURATION_NAME
    os.environ['CONFIGURATION_MAX_AGE_MINUTES'] = '5'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'  # used for appconfig mocked boto calls
    os.environ['TABLE_NAME'] = get_stack_output(TABLE_NAME_OUTPUT)
    os.environ['IDEMPOTENCY_TABLE_NAME'] = get_stack_output(IDEMPOTENCY_TABLE_NAME_OUTPUT)


@pytest.fixture(scope='module', autouse=True)
def table_name():
    return os.environ['TABLE_NAME']
