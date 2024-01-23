from typing import Annotated

from pydantic import BaseModel, Field


class CreateOrderRequest(BaseModel):
    customer_name: Annotated[str, Field(min_length=1, max_length=20, description='Customer name')]
    order_item_count: Annotated[int, Field(gt=0, description='Amount of items in order')]
