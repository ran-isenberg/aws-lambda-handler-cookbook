import pytest
from aws_lambda_powertools.utilities.parser import ValidationError

from service.handlers.schemas.output import Output


def test_invalid_success():
    with pytest.raises(ValidationError):
        Output(success=4, order_item_count=4)


def test_invalid_items():
    with pytest.raises(ValidationError):
        Output(success=4, order_item_count=1.1)


def test_invalid_items_negative():
    with pytest.raises(ValidationError):
        Output(success=4, order_item_count='-1')


def test_invalid_items_zero():
    with pytest.raises(ValidationError):
        Output(success=4, order_item_count=0)


def test_valid_output():
    Output(success=True, order_item_count=4)
