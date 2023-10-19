from typing import Annotated

from pydantic import BaseModel, Field, PositiveInt

from service.models.order import OrderId


class OrderEntry(BaseModel):
    id: OrderId  # primary key
    name: Annotated[str, Field(min_length=1, max_length=20)]
    item_count: PositiveInt
    created_at: PositiveInt
