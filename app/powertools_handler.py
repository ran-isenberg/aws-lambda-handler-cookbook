from typing import List, Literal, Optional
from uuid import UUID

from aws_lambda_powertools.utilities.parser import BaseModel, event_parser
from aws_lambda_powertools.utilities.parser.envelopes import SqsEnvelope
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import PositiveInt, conlist, validator


class OrderItem(BaseModel):
    id: UUID
    quantity: PositiveInt
    description: str
    type: Literal["ACCESSORIES", "COMPUTER"]

class Order(BaseModel):
    id: UUID
    description: str
    items: conlist(OrderItem, min_items=1)
    optional_field: Optional[str]



@event_parser(model=Order, envelope=SqsEnvelope)
def lambda_handler(event: List[Order], context: LambdaContext) -> None:
    write_order(event)


def write_order(order: Order):
    pass
