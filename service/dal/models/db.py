from typing import Annotated

from pydantic import BaseModel, Field, PositiveInt

from service.models.order import OrderId


class OrderEntry(BaseModel):
    """Pydantic model for order entries in DynamoDB."""

    owner_id: Annotated[str, Field(min_length=1)]  # partition key, the access token sub claim of the user that owns the order
    id: OrderId  # sort key
    name: Annotated[str, Field(min_length=1, max_length=20)]
    item_count: PositiveInt
    created_at: PositiveInt
