from typing import Annotated, List, Union

from pydantic import BaseModel, Field

from service.models.order import Order


# create order handler returns this output model, which is similar to the Order model
# but it does not have to be like that in the future.
# The output can be a subject of what order contains, i.e just the id
class CreateOrderOutput(Order):
    pass


class InternalServerErrorOutput(BaseModel):
    error: Annotated[str, Field(description='Error description')] = 'internal server error'


class PydanticError(BaseModel):
    loc: Annotated[List[Union[str, int]], Field(description='Error location')]
    type: Annotated[str, Field(description='Error type')]
    msg: Annotated[str, Field(description='Error message')] = ''


class InvalidRestApiRequest(BaseModel):
    details: Annotated[List[PydanticError], Field(description='Error details')]
