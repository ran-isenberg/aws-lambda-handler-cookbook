from uuid import UUID

from pydantic import BaseModel, PositiveInt, constr, validator


class Output(BaseModel):
    order_item_count: PositiveInt
    customer_name: constr(min_length=1, max_length=20)
    order_id: str

    @validator('order_id')
    def valid_uuid(cls, v):
        UUID(v, version=4)
        return v
