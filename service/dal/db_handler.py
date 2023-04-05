import uuid

import boto3
from botocore.exceptions import ClientError
from cachetools import TTLCache, cached
from mypy_boto3_dynamodb import DynamoDBServiceResource
from mypy_boto3_dynamodb.service_resource import Table
from pydantic import ValidationError

from service.dal.schemas.db import OrderEntry
from service.handlers.utils.observability import logger, tracer
from service.schemas.exceptions import InternalServerException


# cache dynamodb connection data for no longer than 5 minutes
@cached(cache=TTLCache(maxsize=1, ttl=300))
def _get_db_handler(table_name: str) -> Table:
    dynamodb: DynamoDBServiceResource = boto3.resource('dynamodb')
    return dynamodb.Table(table_name)


@tracer.capture_method(capture_response=False)
def create_order_in_db(table_name: str, customer_name: str, order_item_count: int) -> OrderEntry:
    order_id = str(uuid.uuid4())
    logger.info('trying to save order', extra={'order_id': order_id})
    try:
        entry = OrderEntry(order_id=order_id, customer_name=customer_name, order_item_count=order_item_count)
        logger.info('opening connection to dynamodb table', extra={'table_name': table_name})
        table: Table = _get_db_handler(table_name)
        table.put_item(Item=entry.dict())
    except (ClientError, ValidationError) as exc:
        error_msg = 'failed to create order'
        logger.exception(error_msg, extra={'exception': str(exc), 'customer_name': customer_name})
        raise InternalServerException(error_msg) from exc

    logger.info('finished create order', extra={'order_id': order_id, 'order_item_count': order_item_count, 'customer_name': customer_name})
    return entry
