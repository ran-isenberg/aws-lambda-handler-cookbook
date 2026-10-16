from typing import Annotated, Any

from aws_lambda_env_modeler import get_environment_variables, init_environment_variables
from aws_lambda_powertools.event_handler.openapi.params import Body
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext

from service.handlers.models.dynamic_configuration import MyConfiguration
from service.handlers.models.env_vars import MyHandlerEnvVars
from service.handlers.utils.auth import AUTH_RESPONSES, BEARER_SECURITY, REQUIRE_WRITE
from service.handlers.utils.caller import get_caller_id
from service.handlers.utils.dynamic_configuration import parse_configuration
from service.handlers.utils.observability import logger, metrics, tracer
from service.handlers.utils.rest_api_resolver import ORDERS_PATH, app
from service.logic.create_order import create_order
from service.models.input import CreateOrderRequest, OwnedCreateOrderRequest
from service.models.output import CreateOrderOutput, InternalServerErrorOutput


@app.post(
    ORDERS_PATH,
    summary='Create an order',
    description='Create an order identified by the body payload, owned by the caller',
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
        **AUTH_RESPONSES,
    },
    tags=['CRUD'],
    security=BEARER_SECURITY,
    middlewares=REQUIRE_WRITE,
)
def handle_create_order(create_input: Annotated[CreateOrderRequest, Body(embed=False, media_type='application/json')]) -> CreateOrderOutput:
    env_vars: MyHandlerEnvVars = get_environment_variables(model=MyHandlerEnvVars)
    logger.debug('environment variables', env_vars=env_vars.model_dump())
    owner_id = get_caller_id()
    logger.append_keys(owner_id=owner_id)
    logger.info('got create order request', order=create_input.model_dump())

    my_configuration = parse_configuration(model=MyConfiguration)
    logger.debug('fetched dynamic configuration', configuration=my_configuration.model_dump())

    metrics.add_metric(name='ValidCreateOrderEvents', unit=MetricUnit.Count, value=1)
    response: CreateOrderOutput = create_order(
        order_request=OwnedCreateOrderRequest(**create_input.model_dump(), owner_id=owner_id),
        table_name=env_vars.TABLE_NAME,
        context=app.lambda_context,
    )

    logger.info('finished handling create order request')
    return response


@init_environment_variables(model=MyHandlerEnvVars)
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@metrics.log_metrics
@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    return app.resolve(event, context)
