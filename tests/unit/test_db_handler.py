import pytest
from botocore.stub import Stubber

from service.dal.dynamo_dal_handler import DynamoDalHandler
from service.schemas.exceptions import InternalServerException


def test_raise_exception():
    db_handler: DynamoDalHandler = DynamoDalHandler('table')
    table = db_handler._get_db_handler()
    stubber = Stubber(table.meta.client)
    stubber.add_client_error(method='put_item', service_error_code='ValidationException')
    stubber.activate()
    with pytest.raises(InternalServerException):
        db_handler.create_order_in_db(customer_name='customer', order_item_count=5)
