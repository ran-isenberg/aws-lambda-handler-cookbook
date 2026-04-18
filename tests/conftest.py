import uuid
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any

import pytest
from pydynox import DynamoDBClient, dynamodb_model

from cdk.service.constants import TABLE_NAME_OUTPUT
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


def delete_order_from_db(table_name: str, order_id: str) -> None:
    """Delete an order directly from DynamoDB via pydynox. Silent if already gone."""
    entry = _get_order_model(table_name).sync_get(id=order_id)
    if entry is not None:
        entry.sync_delete()


@pytest.fixture(scope='module')
def table_name():
    return get_stack_output(TABLE_NAME_OUTPUT)


@pytest.fixture
def order_factory(table_name):
    """Create orders directly in DynamoDB and delete them automatically at test teardown."""
    created_ids: list[str] = []

    def _create(customer_name: str, order_item_count: int) -> dict[str, Any]:
        order = create_order_in_db(table_name, customer_name, order_item_count)
        created_ids.append(order['id'])
        return order

    yield _create

    for order_id in created_ids:
        delete_order_from_db(table_name, order_id)


@pytest.fixture
def tracked_order_ids(table_name):
    """Append order ids created by the test; teardown deletes them from DynamoDB."""
    ids: list[str] = []
    yield ids
    for order_id in ids:
        delete_order_from_db(table_name, order_id)
