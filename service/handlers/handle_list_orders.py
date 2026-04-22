from typing import Annotated, Any

from aws_lambda_env_modeler import get_environment_variables, init_environment_variables
from aws_lambda_powertools.event_handler.openapi.params import Query
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext

from service.handlers.models.env_vars import ListHandlerEnvVars
from service.handlers.utils.observability import logger, metrics, tracer
from service.handlers.utils.rest_api_resolver import ORDERS_PATH, app
from service.logic.list_orders import list_orders
from service.models.output import InternalServerErrorOutput, InvalidNextTokenOutput, ListOrdersOutput


@app.get(
    ORDERS_PATH,
    summary='List orders',
    description='List orders with pagination. Pass the returned next_token to fetch the next page.',
    response_description='A page of orders and an optional next_token cursor',
    responses={
        200: {
            'description': 'A page of orders',
            'content': {'application/json': {'model': ListOrdersOutput}},
        },
        400: {
            'description': 'Invalid next_token',
            'content': {'application/json': {'model': InvalidNextTokenOutput}},
        },
        501: {
            'description': 'Internal server error',
            'content': {'application/json': {'model': InternalServerErrorOutput}},
        },
    },
    tags=['CRUD'],
)
def handle_list_orders(
    limit: Annotated[int, Query(ge=1, le=100, description='Max orders to return per page')] = 10,
    next_token: Annotated[str | None, Query(description='Opaque cursor returned from a previous call')] = None,
) -> ListOrdersOutput:
    env_vars: ListHandlerEnvVars = get_environment_variables(model=ListHandlerEnvVars)
    logger.debug('environment variables', env_vars=env_vars.model_dump())
    logger.info('got list orders request', limit=limit)

    metrics.add_metric(name='ValidListOrdersEvents', unit=MetricUnit.Count, value=1)
    response: ListOrdersOutput = list_orders(table_name=env_vars.TABLE_NAME, limit=limit, next_token=next_token)

    logger.info('finished handling list orders request', order_count=len(response.orders), has_more=response.next_token is not None)
    return response


@init_environment_variables(model=ListHandlerEnvVars)
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@metrics.log_metrics
@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    return app.resolve(event, context)
