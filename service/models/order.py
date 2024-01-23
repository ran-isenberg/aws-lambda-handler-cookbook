from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field
from pydantic.functional_validators import AfterValidator


def validate_product_id(product_id: str) -> str:
    """Validates Product IDs are valid UUIDs

    Parameters
    ----------
    product_id : str
        Product ID as a string

    Returns
    -------
    str
        Validated product ID value

    Raises
    ------
    ValueError
        When a product ID doesn't conform with the UUID spec.
    """
    try:
        UUID(product_id, version=4)
    except Exception as exc:  # pragma: no cover
        raise ValueError(str(exc)) from exc
    return product_id


OrderId = Annotated[str, Field(min_length=36, max_length=36, description='Order ID as UUID'), AfterValidator(validate_product_id)]
"""Unique Product ID, represented and validated as a UUID string."""


class Order(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=20, description='Customer name')]
    item_count: Annotated[int, Field(gt=0, description='Amount of items in order')]
    id: OrderId
