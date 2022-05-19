from pydantic import BaseModel, PositiveInt


class Output(BaseModel):
    success: bool
    order_item_count: PositiveInt
