import uuid

import boto3
from botocore.exceptions import ClientError
from cachetools import TTLCache, cached
from mypy_boto3_dynamodb import DynamoDBServiceResource
from mypy_boto3_dynamodb.service_resource import Table

from service.handlers.schemas.dynamic_configuration import FeatureFlagsNames
from service.handlers.utils.dynamic_configuration import get_dynamic_configuration_store
from service.handlers.utils.observability import logger, tracer
from service.schemas.exceptions import InternalServerException
from service.schemas.output import Output


@tracer.capture_method(capture_response=False)
def handle_create_request(customer_name: str, order_item_count: int, table_name: str) -> Output:
    logger.info('starting to handle create request', extra={'order_item_count': order_item_count, 'customer_name': customer_name})

    # feature flags example
    config_store = get_dynamic_configuration_store()
    campaign = config_store.evaluate(
        name=FeatureFlagsNames.TEN_PERCENT_CAMPAIGN.value,
        context={},
        default=False,
    )
    logger.debug('campaign feature flag value', extra={'campaign': campaign})
    premium = config_store.evaluate(
        name=FeatureFlagsNames.PREMIUM.value,
        context={'customer_name': customer_name},
        default=False,
    )
    logger.debug('premium feature flag value', extra={'premium': premium})

    return _create_order_in_db(table_name, customer_name, order_item_count)


# cache dynamodb connection data for no longer than 5 minutes
@cached(cache=TTLCache(maxsize=1, ttl=300))
def _get_db_handler(table_name: str) -> Table:
    dynamodb: DynamoDBServiceResource = boto3.resource('dynamodb')
    logger.info('opening connection to dynamodb table', extra={'table_name': table_name})
    return dynamodb.Table(table_name)


def _create_order_in_db(table_name: str, customer_name: str, order_item_count: int):
    order_id = str(uuid.uuid4())
    try:
        table: Table = _get_db_handler(table_name)
        table.put_item(Item={'order_id': order_id, 'customer_name': customer_name, 'count': order_item_count})
    except ClientError as exc:
        error_msg = 'failed to create order'
        logger.exception(error_msg, extra={'exception': str(exc), 'customer_name': customer_name})
        raise InternalServerException(error_msg) from exc

    logger.info('finished create order', extra={'order_id': order_id, 'order_item_count': order_item_count, 'customer_name': customer_name})
    return Output(customer_name=customer_name, order_item_count=order_item_count, order_id=order_id)
