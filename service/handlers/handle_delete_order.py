from typing import Any

from aws_lambda_env_modeler import get_environment_variables, init_environment_variables
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext

from service.handlers.models.env_vars import GetDeleteHandlerEnvVars
from service.handlers.utils.observability import logger, metrics, tracer
from service.handlers.utils.rest_api_resolver import ORDERS_PATH, app
from service.logic.delete_order import delete_order
from service.models.output import DeleteOrderOutput, InternalServerErrorOutput, OrderNotFoundOutput


@app.delete(
    f'{ORDERS_PATH}<order_id>',
    summary='Delete an order',
    description='Delete an order by its ID',
    response_description='The deleted order confirmation',
    responses={
        200: {
            'description': 'Order deleted successfully',
            'content': {'application/json': {'model': DeleteOrderOutput}},
        },
        404: {
            'description': 'Order not found',
            'content': {'application/json': {'model': OrderNotFoundOutput}},
        },
        501: {
            'description': 'Internal server error',
            'content': {'application/json': {'model': InternalServerErrorOutput}},
        },
    },
    tags=['CRUD'],
)
def handle_delete_order(order_id: str) -> DeleteOrderOutput:
    env_vars: GetDeleteHandlerEnvVars = get_environment_variables(model=GetDeleteHandlerEnvVars)
    logger.debug('environment variables', env_vars=env_vars.model_dump())
    logger.append_keys(order_id=order_id)
    logger.info('got delete order request')

    metrics.add_metric(name='ValidDeleteOrderEvents', unit=MetricUnit.Count, value=1)
    response: DeleteOrderOutput = delete_order(
        order_id=order_id,
        table_name=env_vars.TABLE_NAME,
    )

    logger.info('finished handling delete order request')
    return response


@init_environment_variables(model=GetDeleteHandlerEnvVars)
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@metrics.log_metrics
@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    return app.resolve(event, context)
