import uuid
from datetime import datetime

import boto3
from botocore.exceptions import ClientError
from cachetools import TTLCache, cached
from mypy_boto3_dynamodb import DynamoDBServiceResource
from mypy_boto3_dynamodb.service_resource import Table
from pydantic import ValidationError

from service.dal.db_handler import DalHandler
from service.dal.models.db import OrderEntry
from service.handlers.utils.observability import logger, tracer
from service.models.exceptions import InternalServerException
from service.models.order import Order


class DynamoDalHandler(DalHandler):
    def __init__(self, table_name: str):
        self.table_name = table_name

    # cache dynamodb connection data for no longer than 5 minutes
    @cached(cache=TTLCache(maxsize=1, ttl=300))
    def _get_db_handler(self, table_name: str) -> Table:
        logger.info('opening connection to dynamodb table', table_name=table_name)
        dynamodb: DynamoDBServiceResource = boto3.resource('dynamodb')
        return dynamodb.Table(table_name)

    def _get_unix_time(self) -> int:
        return int(datetime.utcnow().timestamp())

    @tracer.capture_method(capture_response=False)
    def create_order_in_db(self, customer_name: str, order_item_count: int) -> Order:
        order_id = str(uuid.uuid4())
        logger.append_keys(order_id=order_id)
        logger.info('trying to save order', customer_name=customer_name, order_item_count=order_item_count)
        try:
            entry = OrderEntry(
                id=order_id,
                name=customer_name,
                item_count=order_item_count,
                created_at=self._get_unix_time(),
            )
            table: Table = self._get_db_handler(self.table_name)
            table.put_item(Item=entry.model_dump())
        except (ClientError, ValidationError) as exc:  # pragma: no cover
            error_msg = 'failed to create order'
            logger.exception(error_msg, customer_name=customer_name)
            raise InternalServerException(error_msg) from exc

        logger.info('finished create order successfully', order_item_count=order_item_count, customer_name=customer_name)
        return Order(id=entry.id, name=entry.name, item_count=entry.item_count)
