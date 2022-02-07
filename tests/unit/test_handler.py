from http import HTTPStatus

from service.my_handler import my_handler
from aws_lambda_powertools.utilities.typing import LambdaContext

def generate_context() -> LambdaContext:
    context = LambdaContext()
    context._aws_request_id = '888888'
    return context


def test_handler_200_ok():
    response = my_handler({}, generate_context())
    assert response['statusCode'] == HTTPStatus.OK
