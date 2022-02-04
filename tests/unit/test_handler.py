from http import HTTPStatus

from aws_lambda_context import LambdaContext
from service.my_handler import my_handler


def generate_context() -> LambdaContext:
    context = LambdaContext()
    context.aws_request_id = '888888'
    return context


def test_handler_200_ok():
    response = my_handler({}, generate_context())
    assert response['statusCode'] == HTTPStatus.OK
