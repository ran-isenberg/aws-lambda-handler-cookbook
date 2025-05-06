from aws_lambda_powertools.utilities.idempotency import idempotent_function
from aws_lambda_powertools.utilities.idempotency.serialization.pydantic import PydanticSerializer
from aws_lambda_powertools.utilities.typing import LambdaContext

from service.dal import get_dal_handler
from service.dal.db_handler import DalHandler
from service.handlers.utils.observability import logger, tracer
from service.logic.utils.idempotency import IDEMPOTENCY_CONFIG, IDEMPOTENCY_LAYER
from service.models.exceptions import OrderNotFoundException
from service.models.input import DeleteOrderRequest
from service.models.order import Order
from service.models.output import DeleteOrderOutput


@idempotent_function(
    data_keyword_argument='delete_request',
    config=IDEMPOTENCY_CONFIG,
    persistence_store=IDEMPOTENCY_LAYER,
    output_serializer=PydanticSerializer,
)
@tracer.capture_method(capture_response=False)
def delete_order(delete_request: DeleteOrderRequest, table_name: str, context: LambdaContext) -> DeleteOrderOutput:
    IDEMPOTENCY_CONFIG.register_lambda_context(context)  # see Lambda timeouts section

    logger.info('starting to handle delete request', order_id=delete_request.order_id)

    dal_handler: DalHandler = get_dal_handler(table_name)
    try:
        order: Order = dal_handler.delete_order_in_db(delete_request.order_id)
        # convert from order object to output, they won't always be the same
        return DeleteOrderOutput(name=order.name, item_count=order.item_count, id=order.id)
    except OrderNotFoundException as exc:
        logger.exception('order not found', order_id=delete_request.order_id)
        raise exc