from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, PositiveInt, field_validator


class OrderEntry(BaseModel):
    order_item_count: PositiveInt
    customer_name: Annotated[str, Field(min_length=1, max_length=20)]
    order_id: str  # primary key

    @field_validator('order_id')
    def valid_uuid(cls, v):
        try:
            UUID(v, version=4)
        except Exception as exc:
            raise ValueError(str(exc))
        return v
