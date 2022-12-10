import pytest
from botocore.exceptions import ClientError

from service.logic.handle_create_request import _create_order_in_db
from service.schemas.exceptions import InternalServerException


def test_raise_exception(mocker):

    def db_mock_function(table_name: str):
        raise ClientError(error_response={}, operation_name='put_item')

    db_mock = mocker.patch('service.logic.handle_create_request._get_db_handler')
    db_mock.side_effect = db_mock_function
    with pytest.raises(InternalServerException):
        _create_order_in_db(table_name='table', customer_name='customer', order_item_count=5)
    db_mock.assert_called
