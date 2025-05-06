from aws_lambda_powertools.utilities.idempotency import idempotent_function
from aws_lambda_powertools.utilities.idempotency.serialization.pydantic import PydanticSerializer
from aws_lambda_powertools.utilities.typing import LambdaContext

from service.dal import get_dal_handler
from service.dal.db_handler import DalHandler
from service.handlers.utils.observability import logger, tracer
from service.logic.utils.idempotency import IDEMPOTENCY_CONFIG, IDEMPOTENCY_LAYER
from service.models.input import DeleteOrderRequest
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

    dal_handler: DalHandler = get_dal_handler(table_name=table_name)
    
    # Delete the order from the database
    dal_handler.delete_order(order_id=delete_request.order_id)
    
    logger.info('successfully deleted order', order_id=delete_request.order_id)

    return DeleteOrderOutput(order_id=delete_request.order_id)