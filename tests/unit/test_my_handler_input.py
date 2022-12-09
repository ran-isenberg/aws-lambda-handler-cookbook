import pytest
from aws_lambda_powertools.utilities.parser import ValidationError

from service.handlers.schemas.input import Input


def test_invalid_name():
    with pytest.raises(ValidationError):
        Input(customer_name='', order_item_count=4)


def test_invalid_name_too_long():
    with pytest.raises(ValidationError):
        Input(customer_name='1234567890112123423232323232323', order_item_count=4)


def test_missing_mandatory_fields():
    with pytest.raises(ValidationError):
        Input(customer_name='a')


def test_invalid_order_number():
    with pytest.raises(ValidationError):
        Input(customer_name='a', order_item_count=-1)


def test_invalid_order_number_type():
    with pytest.raises(ValidationError):
        Input(customer_name='a', order_item_count='a')
