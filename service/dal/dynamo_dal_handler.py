import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import ValidationError
from pydynox import DynamoDBClient, dynamodb_model

from service.dal.db_handler import DalHandler
from service.dal.models.db import OrderEntry
from service.handlers.utils.observability import logger, tracer
from service.models.exceptions import InternalServerException
from service.models.order import Order


class DynamoDalHandler(DalHandler):
    def __init__(self, table_name: str):
        self.table_name = table_name
        self._client = DynamoDBClient()
        self._order_model: Any = None

    def _get_order_model(self) -> Any:
        """Get or create the pydynox-decorated OrderEntry model.

        Returns:
            A pydynox-decorated Pydantic model class bound to the table.
        """
        if self._order_model is None:

            @dynamodb_model(table=self.table_name, hash_key='id', client=self._client)
            class DynamoOrderEntry(OrderEntry):
                pass

            self._order_model = DynamoOrderEntry
        return self._order_model

    def _get_unix_time(self) -> int:
        return int(datetime.now(timezone.utc).timestamp())

    @tracer.capture_method(capture_response=False)
    def create_order_in_db(self, customer_name: str, order_item_count: int) -> Order:
        order_id = str(uuid.uuid4())
        logger.append_keys(order_id=order_id)
        logger.info('trying to save order', customer_name=customer_name, order_item_count=order_item_count)
        try:
            entry = self._get_order_model()(
                id=order_id,
                name=customer_name,
                item_count=order_item_count,
                created_at=self._get_unix_time(),
            )
            entry.save()
        except (ValidationError, Exception) as exc:  # pragma: no cover
            error_msg = 'failed to create order'
            logger.exception(error_msg, customer_name=customer_name)
            raise InternalServerException(error_msg) from exc

        logger.info('finished create order successfully', order_item_count=order_item_count, customer_name=customer_name)
        return Order(id=entry.id, name=entry.name, item_count=entry.item_count)
