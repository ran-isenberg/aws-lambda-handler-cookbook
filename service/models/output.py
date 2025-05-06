from typing import Annotated

from pydantic import BaseModel, Field

from service.models.order import Order


# create order handler returns this output model, which is similar to the Order model
# but it does not have to be like that in the future.
# The output can be a subject of what order contains, i.e just the id
class CreateOrderOutput(Order):
    pass


class DeleteOrderOutput(Order):
    """Output payload for delete order operation."""


class InternalServerErrorOutput(BaseModel):
    error: Annotated[str, Field(description='Error description')] = 'internal server error'
