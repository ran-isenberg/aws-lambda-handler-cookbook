import pytest
from pydantic import ValidationError

from service.models.output import CreateOrderOutput, DeleteOrderOutput, InternalServerErrorOutput


class TestCreateOrderOutput:
    def test_valid_create_order_output(self):
        # Given valid inputs
        name = "TestCustomer"
        item_count = 5
        order_id = "12345678-1234-1234-1234-123456789012"

        # When creating a valid output
        output = CreateOrderOutput(
            name=name,
            item_count=item_count,
            id=order_id
        )

        # Then the output should have the expected values
        assert output.name == name
        assert output.item_count == item_count
        assert output.id == order_id

    def test_invalid_item_count(self):
        # Given an invalid item count
        name = "TestCustomer"
        item_count = -1
        order_id = "12345678-1234-1234-1234-123456789012"

        # When trying to create an output with invalid item count
        # Then it should raise a validation error
        with pytest.raises(ValidationError):
            CreateOrderOutput(
                name=name,
                item_count=item_count,
                id=order_id
            )


class TestDeleteOrderOutput:
    def test_valid_delete_order_output(self):
        # Given valid inputs
        name = "TestCustomer"
        item_count = 5
        order_id = "12345678-1234-1234-1234-123456789012"

        # When creating a valid output
        output = DeleteOrderOutput(
            name=name,
            item_count=item_count,
            id=order_id
        )

        # Then the output should have the expected values
        assert output.name == name
        assert output.item_count == item_count
        assert output.id == order_id

    def test_invalid_id(self):
        # Given an invalid order ID
        name = "TestCustomer"
        item_count = 5
        order_id = "invalid-id"

        # When trying to create an output with invalid ID
        # Then it should raise a validation error
        with pytest.raises(ValidationError):
            DeleteOrderOutput(
                name=name,
                item_count=item_count,
                id=order_id
            )


class TestInternalServerErrorOutput:
    def test_default_error_message(self):
        # When creating a default error output
        error_output = InternalServerErrorOutput()

        # Then it should have the default error message
        assert error_output.error == "internal server error"

    def test_custom_error_message(self):
        # Given a custom error message
        custom_error = "custom error message"

        # When creating an error output with a custom message
        error_output = InternalServerErrorOutput(error=custom_error)

        # Then it should have the custom error message
        assert error_output.error == custom_error