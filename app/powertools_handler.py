from typing import List, Optional

from aws_lambda_powertools.utilities.parser import BaseModel, event_parser
from aws_lambda_powertools.utilities.parser.envelopes import SqsEnvelope
from pydantic import validator


class OrderItem(BaseModel):
    id: str
    quantity: int
    description: str

    @validator('quantity')
    def quantity_should_not_be_negative(cls, v):
        if v < 0:
            raise ValueError('must not be negative')
        return v


class Order(BaseModel):
    id: str
    description: str
    items: List[OrderItem]
    optional_field: Optional[str]


@event_parser(model=Order, envelope=SqsEnvelope)
def lambda_handler(event, context):
    write_order(event)
    pass


def write_order(order):
    pass
