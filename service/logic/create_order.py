from aws_lambda_powertools.utilities.idempotency import idempotent_function
from aws_lambda_powertools.utilities.idempotency.serialization.pydantic import PydanticSerializer
from aws_lambda_powertools.utilities.typing import LambdaContext

from service.dal import get_dal_handler
from service.dal.db_handler import DalHandler
from service.handlers.models.dynamic_configuration import FeatureFlagsNames
from service.handlers.utils.dynamic_configuration import get_configuration_store
from service.handlers.utils.observability import logger, tracer
from service.logic.utils.idempotency import IDEMPOTENCY_CONFIG, IDEMPOTENCY_LAYER
from service.models.input import CreateOrderRequest
from service.models.order import Order
from service.models.output import CreateOrderOutput


@idempotent_function(
    data_keyword_argument='order_request',
    config=IDEMPOTENCY_CONFIG,
    persistence_store=IDEMPOTENCY_LAYER,
    output_serializer=PydanticSerializer,
)
@tracer.capture_method(capture_response=False)
def create_order(order_request: CreateOrderRequest, table_name: str, context: LambdaContext) -> CreateOrderOutput:
    IDEMPOTENCY_CONFIG.register_lambda_context(context)  # see Lambda timeouts section

    logger.info('starting to handle create request', order_item_count=order_request.order_item_count, customer_name=order_request.customer_name)

    # feature flags example
    config_store = get_configuration_store()

    # discount campaign flag
    campaign = config_store.evaluate(
        name=FeatureFlagsNames.TEN_PERCENT_CAMPAIGN.value,
        context={},
        default=False,
    )
    if campaign:
        handle_campaign()
    else:
        logger.debug('campaign is off')

    # premium users flag - changes according to customer name
    premium = config_store.evaluate(
        name=FeatureFlagsNames.PREMIUM.value,
        context={'customer_name': order_request.customer_name},
        default=False,
    )

    logger.debug('premium feature flag value', premium=premium)
    if premium:
        apply_premium_user_discount()

    dal_handler: DalHandler = get_dal_handler(table_name)
    order: Order = dal_handler.create_order_in_db(order_request.customer_name, order_request.order_item_count)
    # convert from order object to output, they won't always be the same
    return CreateOrderOutput(name=order.name, item_count=order.item_count, id=order.id)


def handle_campaign():
    logger.debug('campaign feature flag is on')
    return


def apply_premium_user_discount():
    logger.debug('premium user detected')
    return
