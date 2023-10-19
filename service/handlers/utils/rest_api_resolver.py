import json
from http import HTTPStatus

from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response, content_types
from pydantic import ValidationError

from service.handlers.utils.observability import logger
from service.models.exceptions import DynamicConfigurationException, InternalServerException

ORDERS_PATH = '/api/orders/'

app = APIGatewayRestResolver()


@app.exception_handler(DynamicConfigurationException)
def handle_dynamic_config_error(ex: DynamicConfigurationException):  # receives exception raised
    logger.exception('failed to load dynamic configuration from AppConfig')
    return Response(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content_type=content_types.APPLICATION_JSON,
        body=json.dumps({'error': 'internal server error'}),
    )


@app.exception_handler(ValidationError)
def handle_input_validation_error(ex: ValidationError):  # receives exception raised
    logger.exception('event failed input validation')
    return Response(
        status_code=HTTPStatus.BAD_REQUEST,
        content_type=content_types.APPLICATION_JSON,
        body=json.dumps({'error': 'invalid input'}),  # readiness: change pydantic error to a user friendly error
    )


@app.exception_handler(InternalServerException)
def handle_internal_server_error(ex: InternalServerException):  # receives exception raised
    logger.exception('finished handling request with internal error')
    return Response(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content_type=content_types.APPLICATION_JSON,
        body=json.dumps({'error': 'internal server error'}),
    )
