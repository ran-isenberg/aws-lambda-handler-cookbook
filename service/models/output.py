from typing import Annotated

from pydantic import BaseModel, Field

from service.models.order import Order


# create order handler returns this output model, which is similar to the Order model
# but it does not have to be like that in the future.
# The output can be a subject of what order contains, i.e just the id
class CreateOrderOutput(Order):
    pass


class GetOrderOutput(Order):
    pass


class DeleteOrderOutput(BaseModel):
    order_id: Annotated[str, Field(description='The deleted order ID')]


class InternalServerErrorOutput(BaseModel):
    error: Annotated[str, Field(description='Error description')] = 'internal server error'


class OrderNotFoundOutput(BaseModel):
    error: Annotated[str, Field(description='Error description')] = 'order was not found'


class InvalidNextTokenOutput(BaseModel):
    error: Annotated[str, Field(description='Error description')] = 'invalid next_token'


class ListOrdersOutput(BaseModel):
    orders: Annotated[list[Order], Field(description='Orders in this page')]
    next_token: Annotated[str | None, Field(description='Opaque cursor; pass back as next_token to get the next page')] = None
