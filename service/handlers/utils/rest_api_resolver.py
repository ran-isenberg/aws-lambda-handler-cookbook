from http import HTTPStatus

from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response, content_types
from aws_lambda_powertools.event_handler.openapi.models import HTTPBearer, SecurityScheme

from service.handlers.utils.observability import logger
from service.models.exceptions import DynamicConfigurationException, InternalServerException, InvalidNextTokenException, OrderNotFoundException
from service.models.output import InternalServerErrorOutput, InvalidNextTokenOutput, OrderNotFoundOutput

ORDERS_PATH = '/api/orders/'
OPENAPI_TITLE = 'AWS Lambda Handler Cookbook - Orders Service'
BEARER_SECURITY_SCHEME_NAME = 'bearerAuth'
BEARER_SECURITY_SCHEMES: dict[str, SecurityScheme] = {
    BEARER_SECURITY_SCHEME_NAME: HTTPBearer(bearerFormat='JWT', description='Amazon Cognito access token sent as: Authorization: Bearer <token>')
}

app = APIGatewayRestResolver(enable_validation=True)
# security_schemes is set here (and not only in enable_swagger) so that the OpenAPI merge (make openapi) sees it as well
app.configure_openapi(title=OPENAPI_TITLE, security_schemes=BEARER_SECURITY_SCHEMES)
app.enable_swagger(path='/swagger', title=OPENAPI_TITLE)
app.configure_openapi_merge(
    path='service/handlers/',
    pattern='*/.py',
    resolver_name='app',
    title=OPENAPI_TITLE,
    security_schemes=BEARER_SECURITY_SCHEMES,
)


@app.exception_handler(DynamicConfigurationException)
def handle_dynamic_config_error(ex: DynamicConfigurationException):  # receives exception raised
    logger.exception('failed to load dynamic configuration from AppConfig')
    return Response(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content_type=content_types.APPLICATION_JSON, body=InternalServerErrorOutput().model_dump()
    )


@app.exception_handler(InternalServerException)
def handle_internal_server_error(ex: InternalServerException):  # receives exception raised
    logger.exception('finished handling request with internal error')
    return Response(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content_type=content_types.APPLICATION_JSON, body=InternalServerErrorOutput().model_dump()
    )


@app.exception_handler(OrderNotFoundException)
def handle_order_not_found_error(ex: OrderNotFoundException):  # receives exception raised
    logger.exception('order was not found')
    return Response(status_code=HTTPStatus.NOT_FOUND, content_type=content_types.APPLICATION_JSON, body=OrderNotFoundOutput().model_dump())


@app.exception_handler(InvalidNextTokenException)
def handle_invalid_next_token(ex: InvalidNextTokenException):  # receives exception raised
    logger.info('invalid next_token provided')
    return Response(status_code=HTTPStatus.BAD_REQUEST, content_type=content_types.APPLICATION_JSON, body=InvalidNextTokenOutput().model_dump())
