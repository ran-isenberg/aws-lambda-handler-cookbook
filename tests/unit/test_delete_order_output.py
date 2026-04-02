import uuid

from service.models.output import DeleteOrderOutput


def test_valid_output():
    # Given: A valid order ID
    order_id = str(uuid.uuid4())

    # When: DeleteOrderOutput is initialized
    output = DeleteOrderOutput(order_id=order_id)

    # Then: No exception should be raised and the order_id is set
    assert output.order_id == order_id
