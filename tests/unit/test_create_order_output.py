import uuid

import pytest
from aws_lambda_powertools.utilities.parser import ValidationError

from service.models.output import CreateOrderOutput

id = str(uuid.uuid4())


def test_invalid_items_type():
    # Given: An invalid non-integer item_count
    name = '3333'
    item_count = 'a'

    # When & Then: CreateOrderOutput is initialized, expect a ValidationError
    with pytest.raises(ValidationError):
        CreateOrderOutput(id=id, name=name, item_count=item_count)


def test_invalid_items_negative():
    # Given: An invalid negative item_count
    name = '3333'
    item_count = -1

    # When & Then: CreateOrderOutput is initialized, expect a ValidationError
    with pytest.raises(ValidationError):
        CreateOrderOutput(id=id, name=name, item_count=item_count)


def test_invalid_items_zero():
    # Given: An invalid zero item_count
    name = '3333'
    item_count = 0

    # When & Then: CreateOrderOutput is initialized, expect a ValidationError
    with pytest.raises(ValidationError):
        CreateOrderOutput(id=id, name=name, item_count=item_count)


def test_invalid_id():
    # Given: An invalid id
    id_invalid = '2'
    name = '3333'
    item_count = 2

    # When & Then: CreateOrderOutput is initialized, expect a ValidationError
    with pytest.raises(ValidationError):
        CreateOrderOutput(id=id_invalid, name=name, item_count=item_count)


def test_valid_output():
    # Given: Valid inputs
    name = '222'
    item_count = 4

    # When: CreateOrderOutput is initialized
    # Then: No exception should be raised
    CreateOrderOutput(id=id, name=name, item_count=item_count)
