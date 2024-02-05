from typing import Annotated

from pydantic import BaseModel, Field, field_validator


class CreateOrderRequest(BaseModel):
    customer_name: Annotated[str, Field(min_length=1, max_length=20, description='Customer name')]
    order_item_count: Annotated[int, Field(strict=True, description='Amount of items in order')]

    @field_validator('order_item_count')
    @classmethod
    def check_order_item_count(cls, v):
        # we don't use Field(gt=0) because pydantic exports it incorrectly to openAPI doc
        # see https://github.com/tiangolo/fastapi/issues/240
        if v <= 0:
            raise ValueError('order_item_count must be larger than 0')
        return v
