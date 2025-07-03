import pytest
from pydantic import ValidationError

from service.models.input import CreateOrderRequest, DeleteOrderRequest


class TestCreateOrderRequest:
    def test_valid_create_order_request(self):
        # Given valid inputs
        customer_name = "TestCustomer"
        order_item_count = 5

        # When creating a valid request
        request = CreateOrderRequest(
            customer_name=customer_name,
            order_item_count=order_item_count
        )

        # Then the request should have the expected values
        assert request.customer_name == customer_name
        assert request.order_item_count == order_item_count

    def test_invalid_customer_name(self):
        # Given an empty customer name
        customer_name = ""
        order_item_count = 5

        # When trying to create a request with invalid customer name
        # Then it should raise a validation error
        with pytest.raises(ValidationError):
            CreateOrderRequest(
                customer_name=customer_name,
                order_item_count=order_item_count
            )

    def test_invalid_order_item_count(self):
        # Given a negative order item count
        customer_name = "TestCustomer"
        order_item_count = -1

        # When trying to create a request with invalid order item count
        # Then it should raise a validation error
        with pytest.raises(ValidationError):
            CreateOrderRequest(
                customer_name=customer_name,
                order_item_count=order_item_count
            )

    def test_zero_order_item_count(self):
        # Given a zero order item count
        customer_name = "TestCustomer"
        order_item_count = 0

        # When trying to create a request with zero order item count
        # Then it should raise a validation error
        with pytest.raises(ValidationError):
            CreateOrderRequest(
                customer_name=customer_name,
                order_item_count=order_item_count
            )


class TestDeleteOrderRequest:
    def test_valid_delete_order_request(self):
        # Given a valid order ID (UUID format)
        order_id = "12345678-1234-1234-1234-123456789012"

        # When creating a valid delete request
        request = DeleteOrderRequest(order_id=order_id)

        # Then the request should have the expected value
        assert request.order_id == order_id

    def test_invalid_order_id_too_short(self):
        # Given an order ID that's too short
        order_id = "12345"

        # When trying to create a request with an invalid order ID
        # Then it should raise a validation error
        with pytest.raises(ValidationError):
            DeleteOrderRequest(order_id=order_id)

    def test_invalid_order_id_too_long(self):
        # Given an order ID that's too long
        order_id = "12345678-1234-1234-1234-1234567890123456"

        # When trying to create a request with an invalid order ID
        # Then it should raise a validation error
        with pytest.raises(ValidationError):
            DeleteOrderRequest(order_id=order_id)