import json
from http import HTTPStatus

from service.handlers.my_handler import my_handler
from tests.utils import generate_context


def generate_event(path_name: str) -> Dict:
    return {}


def test_handler_200_ok():
    response = my_handler({}, generate_context())
    assert response['statusCode'] == HTTPStatus.OK
    body_dict = json.loads(response['body'])
    assert body_dict['message'] == 'success'
