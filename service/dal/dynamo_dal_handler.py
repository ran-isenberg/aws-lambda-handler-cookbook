import base64
import json
import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import ValidationError
from pydynox import DynamoDBClient, dynamodb_model

from service.dal.db_handler import DalHandler
from service.dal.models.db import OrderEntry
from service.handlers.utils.observability import logger, tracer
from service.models.exceptions import InternalServerException, InvalidNextTokenException, OrderNotFoundException
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

            @dynamodb_model(table=self.table_name, partition_key='id', client=self._client)
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
            entry.sync_save()
        except (ValidationError, Exception) as exc:  # pragma: no cover
            error_msg = 'failed to create order'
            logger.exception(error_msg, customer_name=customer_name)
            raise InternalServerException(error_msg) from exc

        logger.info('finished create order successfully', order_item_count=order_item_count, customer_name=customer_name)
        return Order(id=entry.id, name=entry.name, item_count=entry.item_count)

    @tracer.capture_method(capture_response=False)
    def get_order_from_db(self, order_id: str) -> Order:
        logger.info('trying to get order')
        try:
            entry = self._get_order_model().sync_get(id=order_id)
        except (ValidationError, Exception) as exc:  # pragma: no cover
            error_msg = 'failed to get order'
            logger.exception(error_msg)
            raise InternalServerException(error_msg) from exc

        if entry is None:
            logger.info('order was not found')
            raise OrderNotFoundException(f'order {order_id} was not found')

        logger.info('finished get order successfully')
        return Order(id=entry.id, name=entry.name, item_count=entry.item_count)

    @tracer.capture_method(capture_response=False)
    def delete_order_from_db(self, order_id: str) -> None:
        logger.info('trying to delete order')
        # first verify order exists
        try:
            entry = self._get_order_model().sync_get(id=order_id)
        except (ValidationError, Exception) as exc:  # pragma: no cover
            error_msg = 'failed to delete order'
            logger.exception(error_msg)
            raise InternalServerException(error_msg) from exc

        if entry is None:
            logger.info('order was not found')
            raise OrderNotFoundException(f'order {order_id} was not found')

        try:
            entry.sync_delete()
        except Exception as exc:  # pragma: no cover
            error_msg = 'failed to delete order'
            logger.exception(error_msg)
            raise InternalServerException(error_msg) from exc

        logger.info('finished delete order successfully')

    @tracer.capture_method(capture_response=False)
    def list_orders_from_db(self, limit: int, next_token: str | None) -> tuple[list[Order], str | None]:
        logger.info('trying to list orders', limit=limit, has_next_token=next_token is not None)
        exclusive_start_key = self._decode_next_token(next_token)
        try:
            result = self._client.sync_scan(
                table=self.table_name,
                limit=limit,
                last_evaluated_key=exclusive_start_key,
            )
            items = list(result)
            last_evaluated_key = result.last_evaluated_key
        except (ValidationError, Exception) as exc:  # pragma: no cover
            error_msg = 'failed to list orders'
            logger.exception(error_msg)
            raise InternalServerException(error_msg) from exc

        orders = [Order(id=item['id'], name=item['name'], item_count=int(item['item_count'])) for item in items]
        new_next_token = self._encode_next_token(last_evaluated_key)
        logger.info('finished list orders successfully', order_count=len(orders), has_more=new_next_token is not None)
        return orders, new_next_token

    @staticmethod
    def _encode_next_token(last_evaluated_key: dict[str, Any] | None) -> str | None:
        if not last_evaluated_key:
            return None
        return base64.urlsafe_b64encode(json.dumps(last_evaluated_key).encode()).decode()

    @staticmethod
    def _decode_next_token(next_token: str | None) -> dict[str, Any] | None:
        if not next_token:
            return None
        try:
            return json.loads(base64.urlsafe_b64decode(next_token.encode()).decode())
        except Exception as exc:
            raise InvalidNextTokenException('invalid next_token') from exc
