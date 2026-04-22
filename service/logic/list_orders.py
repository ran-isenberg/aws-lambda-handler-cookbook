from service.dal import get_dal_handler
from service.dal.db_handler import DalHandler
from service.handlers.utils.observability import logger, tracer
from service.models.output import ListOrdersOutput


@tracer.capture_method(capture_response=False)
def list_orders(table_name: str, limit: int, next_token: str | None) -> ListOrdersOutput:
    logger.info('starting to handle list orders request', limit=limit)

    dal_handler: DalHandler = get_dal_handler(table_name)
    orders, new_next_token = dal_handler.list_orders_from_db(limit=limit, next_token=next_token)
    return ListOrdersOutput(orders=orders, next_token=new_next_token)
