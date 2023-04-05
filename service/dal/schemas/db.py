from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, PositiveInt, validator


class OrderEntry(BaseModel):
    order_item_count: PositiveInt
    customer_name: Annotated[str, Field(min_length=1, max_length=20)]
    order_id: str  # primary key

    @validator('order_id')
    def valid_uuid(cls, v):
        UUID(v, version=4)
        return v
