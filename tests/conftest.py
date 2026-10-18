import uuid
from collections.abc import Iterator
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any

import pytest
from pydynox import DynamoDBClient, dynamodb_model

from cdk.service.constants import MANAGERS_GROUP, TABLE_NAME_OUTPUT
from service.dal.models.db import OrderEntry
from tests.auth_utils import CognitoPool, CognitoUser, bearer_headers, create_cognito_user, delete_cognito_user, get_cognito_pool
from tests.utils import get_stack_output

_dynamo_client = DynamoDBClient()


@lru_cache
def _get_order_model(table_name: str):
    @dynamodb_model(table=table_name, partition_key='owner_id', sort_key='id', client=_dynamo_client)
    class DynamoOrderEntry(OrderEntry):
        pass

    return DynamoOrderEntry


def create_order_in_db(table_name: str, owner_id: str, customer_name: str, order_item_count: int) -> dict[str, Any]:
    """Create an order owned by owner_id directly in DynamoDB via pydynox."""
    order_id = str(uuid.uuid4())
    entry = _get_order_model(table_name)(
        owner_id=owner_id,
        id=order_id,
        name=customer_name,
        item_count=order_item_count,
        created_at=int(datetime.now(timezone.utc).timestamp()),
    )
    entry.sync_save()
    return {'id': order_id, 'name': customer_name, 'item_count': order_item_count}


def get_order_from_db(table_name: str, owner_id: str, order_id: str) -> OrderEntry | None:
    """Get an order directly from DynamoDB via pydynox. Returns None if not found."""
    return _get_order_model(table_name).sync_get(owner_id=owner_id, id=order_id)


def delete_order_from_db(table_name: str, owner_id: str, order_id: str) -> None:
    """Delete an order directly from DynamoDB via pydynox. Silent if already gone."""
    entry = _get_order_model(table_name).sync_get(owner_id=owner_id, id=order_id)
    if entry is not None:
        entry.sync_delete()


@pytest.fixture(scope='module')
def table_name():
    return get_stack_output(TABLE_NAME_OUTPUT)


@pytest.fixture
def order_factory(table_name):
    """Create orders owned by a user directly in DynamoDB and delete them automatically at test teardown."""
    created: list[tuple[str, str]] = []

    def _create(owner: CognitoUser, customer_name: str, order_item_count: int) -> dict[str, Any]:
        order = create_order_in_db(table_name, owner.sub, customer_name, order_item_count)
        created.append((owner.sub, order['id']))
        return order

    yield _create

    for owner_id, order_id in created:
        delete_order_from_db(table_name, owner_id, order_id)


@pytest.fixture
def tracked_orders(table_name):
    """Append the (owner_id, order_id) of orders created by the test; teardown deletes them from DynamoDB."""
    orders: list[tuple[str, str]] = []
    yield orders
    for owner_id, order_id in orders:
        delete_order_from_db(table_name, owner_id, order_id)


# Cognito users are created once per test session (not per test), and deleted when the session ends.
# Tests receive the ready to use 'Authorization: Bearer <access token>' headers through the *_headers fixtures.
@pytest.fixture(scope='session')
def cognito_pool() -> CognitoPool:
    return get_cognito_pool()


@pytest.fixture(scope='session')
def manager_user(cognito_pool: CognitoPool) -> Iterator[CognitoUser]:
    """In the managers group (orders/manage scope): can create, get, list and delete their own orders."""
    user = create_cognito_user(cognito_pool, [MANAGERS_GROUP])
    yield user
    delete_cognito_user(cognito_pool, user.username)


@pytest.fixture(scope='session')
def other_manager_user(cognito_pool: CognitoPool) -> Iterator[CognitoUser]:
    """A second manager, to verify that users can't reach each other's orders."""
    user = create_cognito_user(cognito_pool, [MANAGERS_GROUP])
    yield user
    delete_cognito_user(cognito_pool, user.username)


@pytest.fixture(scope='session')
def member_user(cognito_pool: CognitoPool) -> Iterator[CognitoUser]:
    """A signed in user in no group (no scope): can get and list their own orders, can't create or delete orders."""
    user = create_cognito_user(cognito_pool, [])
    yield user
    delete_cognito_user(cognito_pool, user.username)


@pytest.fixture(scope='session')
def manager_headers(manager_user: CognitoUser) -> dict[str, str]:
    return bearer_headers(manager_user.access_token)


@pytest.fixture(scope='session')
def other_manager_headers(other_manager_user: CognitoUser) -> dict[str, str]:
    return bearer_headers(other_manager_user.access_token)


@pytest.fixture(scope='session')
def member_headers(member_user: CognitoUser) -> dict[str, str]:
    return bearer_headers(member_user.access_token)
