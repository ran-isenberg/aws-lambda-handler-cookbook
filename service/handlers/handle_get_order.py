from typing import Any

from aws_lambda_env_modeler import get_environment_variables, init_environment_variables
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext

from service.handlers.models.env_vars import GetHandlerEnvVars
from service.handlers.utils.auth import AUTH_RESPONSES, BEARER_SECURITY, REQUIRE_READ
from service.handlers.utils.caller import get_caller_id
from service.handlers.utils.observability import logger, metrics, tracer
from service.handlers.utils.rest_api_resolver import ORDERS_PATH, app
from service.logic.get_order import get_order
from service.models.output import GetOrderOutput, InternalServerErrorOutput, OrderNotFoundOutput


@app.get(
    f'{ORDERS_PATH}<order_id>',
    summary='Get an order',
    description='Get an order of the caller by its ID',
    response_description='The requested order',
    responses={
        200: {
            'description': 'The requested order',
            'content': {'application/json': {'model': GetOrderOutput}},
        },
        404: {
            'description': 'Order not found (or owned by another user)',
            'content': {'application/json': {'model': OrderNotFoundOutput}},
        },
        501: {
            'description': 'Internal server error',
            'content': {'application/json': {'model': InternalServerErrorOutput}},
        },
        **AUTH_RESPONSES,
    },
    tags=['CRUD'],
    security=BEARER_SECURITY,
    middlewares=REQUIRE_READ,
)
def handle_get_order(order_id: str) -> GetOrderOutput:
    env_vars: GetHandlerEnvVars = get_environment_variables(model=GetHandlerEnvVars)
    logger.debug('environment variables', env_vars=env_vars.model_dump())
    owner_id = get_caller_id()
    logger.append_keys(order_id=order_id, owner_id=owner_id)
    logger.info('got get order request')

    metrics.add_metric(name='ValidGetOrderEvents', unit=MetricUnit.Count, value=1)
    response: GetOrderOutput = get_order(
        owner_id=owner_id,
        order_id=order_id,
        table_name=env_vars.TABLE_NAME,
    )

    logger.info('finished handling get order request')
    return response


@init_environment_variables(model=GetHandlerEnvVars)
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@metrics.log_metrics
@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    return app.resolve(event, context)
