import json
from http import HTTPStatus

from service.handlers.my_handler import my_handler
from tests.utils import generate_api_gw_event, generate_context


def test_handler_200_ok():
    response = my_handler(generate_api_gw_event(), generate_context())
    assert response['statusCode'] == HTTPStatus.OK
    body_dict = json.loads(response['body'])
    assert body_dict['message'] == 'success'
    assert False
