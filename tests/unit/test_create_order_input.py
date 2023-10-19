import pytest
from aws_lambda_powertools.utilities.parser import ValidationError

from service.models.input import CreateOrderRequest

# ... potentially more imports based on your project ...


def test_invalid_name():
    # Given: An empty customer_name
    customer_name = ''
    order_item_count = 4

    # When & Then: CreateOrderRequest is initialized, expect a ValidationError
    with pytest.raises(ValidationError):
        CreateOrderRequest(customer_name=customer_name, order_item_count=order_item_count)


def test_invalid_name_too_long():
    # Given: A too long customer_name
    customer_name = '1' * 33  # or '1234567890112123423232323232323' based on your original code
    order_item_count = 4

    # When & Then: CreateOrderRequest is initialized, expect a ValidationError
    with pytest.raises(ValidationError):
        CreateOrderRequest(customer_name=customer_name, order_item_count=order_item_count)


def test_missing_mandatory_fields():
    # Given: A missing order_item_count
    customer_name = 'a'

    # When & Then: CreateOrderRequest is initialized, expect a ValidationError
    with pytest.raises(ValidationError):
        CreateOrderRequest(customer_name=customer_name)


def test_invalid_order_number():
    # Given: An invalid negative order_item_count
    customer_name = 'a'
    order_item_count = -1

    # When & Then: CreateOrderRequest is initialized, expect a ValidationError
    with pytest.raises(ValidationError):
        CreateOrderRequest(customer_name=customer_name, order_item_count=order_item_count)


def test_invalid_order_number_type():
    # Given: A non-integer order_item_count
    customer_name = 'a'
    order_item_count = 'a'

    # When & Then: CreateOrderRequest is initialized, expect a ValidationError
    with pytest.raises(ValidationError):
        CreateOrderRequest(customer_name=customer_name, order_item_count=order_item_count)
