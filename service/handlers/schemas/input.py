from pydantic import BaseModel, PositiveInt, constr


class Input(BaseModel):
    customer_name: constr(min_length=1, max_length=20)
    order_item_count: PositiveInt
