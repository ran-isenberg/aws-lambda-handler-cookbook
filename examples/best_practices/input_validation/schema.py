from typing import Annotated

from pydantic import BaseModel, Field, PositiveInt


class Input(BaseModel):
    customer_name: Annotated[str, Field(min_length=1, max_length=20)]
    order_item_count: PositiveInt
