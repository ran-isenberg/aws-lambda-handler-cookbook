import json
from http import HTTPStatus

from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response, content_types

from service.handlers.utils.observability import logger
from service.models.exceptions import DynamicConfigurationException, InternalServerException

ORDERS_PATH = '/api/orders/'

app = APIGatewayRestResolver(enable_validation=True)
app.enable_swagger(path='/swagger')


@app.exception_handler(DynamicConfigurationException)
def handle_dynamic_config_error(ex: DynamicConfigurationException):  # receives exception raised
    logger.exception('failed to load dynamic configuration from AppConfig')
    return Response(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content_type=content_types.APPLICATION_JSON,
        body=json.dumps({'error': 'internal server error'}),
    )


@app.exception_handler(InternalServerException)
def handle_internal_server_error(ex: InternalServerException):  # receives exception raised
    logger.exception('finished handling request with internal error')
    return Response(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content_type=content_types.APPLICATION_JSON,
        body=json.dumps({'error': 'internal server error'}),
    )
