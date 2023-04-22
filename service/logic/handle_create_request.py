from service.dal.db_handler import DalHandler
from service.dal.dynamo_dal_handler import get_dal_handler
from service.dal.schemas.db import OrderEntry
from service.handlers.schemas.dynamic_configuration import FeatureFlagsNames
from service.handlers.utils.dynamic_configuration import get_dynamic_configuration_store
from service.handlers.utils.observability import logger, tracer
from service.schemas.output import CreateOrderOutput


@tracer.capture_method(capture_response=False)
def handle_create_request(customer_name: str, order_item_count: int, table_name: str) -> CreateOrderOutput:
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
    dal_handler: DalHandler = get_dal_handler(table_name)
    order: OrderEntry = dal_handler.create_order_in_db(customer_name, order_item_count)
    # convert from db entry to output, they won't always be the same
    return CreateOrderOutput(customer_name=order.customer_name, order_item_count=order.order_item_count, order_id=order.order_id)
