from http import HTTPStatus
from typing import Any

from aws_lambda_env_modeler import get_environment_variables, init_environment_variables
from aws_lambda_powertools.event_handler import BedrockAgentResolver, Response, content_types
from aws_lambda_powertools.event_handler.openapi.params import Body
from aws_lambda_powertools.shared.types import Annotated
from aws_lambda_powertools.utilities.typing import LambdaContext

from service.handlers.models.env_vars import MyHandlerEnvVars
from service.handlers.utils.observability import logger
from service.logic.create_order import create_order
from service.models.exceptions import InternalServerException
from service.models.input import CreateOrderRequest
from service.models.output import CreateOrderOutput, InternalServerErrorOutput

ORDERS_PATH = '/api/orders/'

app = BedrockAgentResolver()


@app.exception_handler(InternalServerException)
def handle_internal_server_error(ex: InternalServerException):  # receives exception raised
    logger.exception('finished handling request with internal error')
    return Response(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content_type=content_types.APPLICATION_JSON, body=InternalServerErrorOutput().model_dump()
    )


@app.post(
    ORDERS_PATH,
    summary='Create an order',
    description='Create an order identified by the body payload',
    response_description='The created order',
    responses={
        200: {
            'description': 'The created order',
            'content': {'application/json': {'model': CreateOrderOutput}},
        },
        501: {
            'description': 'Internal server error',
            'content': {'application/json': {'model': InternalServerErrorOutput}},
        },
    },
    tags=['CRUD'],
)
def handle_create_order(create_input: Annotated[CreateOrderRequest, Body(embed=False, media_type='application/json')]) -> CreateOrderOutput:
    env_vars: MyHandlerEnvVars = get_environment_variables(model=MyHandlerEnvVars)
    logger.debug('environment variables', env_vars=env_vars.model_dump())
    logger.info('got create order request', order=create_input.model_dump())

    response: CreateOrderOutput = create_order(
        order_request=create_input,
        table_name=env_vars.TABLE_NAME,
        context=app.lambda_context,
    )

    logger.info('finished handling create order request')
    return response


@init_environment_variables(model=MyHandlerEnvVars)
@logger.inject_lambda_context(log_event=True)
def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    return app.resolve(event, context)
