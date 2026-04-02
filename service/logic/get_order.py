from service.dal import get_dal_handler
from service.dal.db_handler import DalHandler
from service.handlers.utils.observability import logger, tracer
from service.models.order import Order
from service.models.output import GetOrderOutput


@tracer.capture_method(capture_response=False)
def get_order(order_id: str, table_name: str) -> GetOrderOutput:
    logger.info('starting to handle get order request', order_id=order_id)

    dal_handler: DalHandler = get_dal_handler(table_name)
    order: Order = dal_handler.get_order_from_db(order_id)
    # convert from order object to output, they won't always be the same
    return GetOrderOutput(name=order.name, item_count=order.item_count, id=order.id)
