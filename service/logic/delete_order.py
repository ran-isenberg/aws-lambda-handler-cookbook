from service.dal import get_dal_handler
from service.dal.db_handler import DalHandler
from service.handlers.utils.observability import logger, tracer
from service.models.output import DeleteOrderOutput


@tracer.capture_method(capture_response=False)
def delete_order(order_id: str, table_name: str) -> DeleteOrderOutput:
    logger.info('starting to handle delete order request', order_id=order_id)

    dal_handler: DalHandler = get_dal_handler(table_name)
    dal_handler.delete_order_from_db(order_id)
    return DeleteOrderOutput(order_id=order_id)
