from http import HTTPStatus
from typing import Annotated, Any

from aws_lambda_env_modeler import get_environment_variables, init_environment_variables
from aws_lambda_powertools.event_handler import Response, content_types
from aws_lambda_powertools.event_handler.openapi.params import Body
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext

from service.handlers.models.env_vars import MyHandlerEnvVars
from service.handlers.utils.observability import logger, metrics, tracer
from service.handlers.utils.rest_api_resolver import ORDERS_PATH, app
from service.logic.delete_order import delete_order
from service.models.exceptions import OrderNotFoundException
from service.models.input import DeleteOrderRequest
from service.models.output import DeleteOrderOutput, InternalServerErrorOutput, OrderNotFoundOutput


@app.post(
    f"{ORDERS_PATH}delete",
    summary='Delete an order',
    description='Delete an order identified by the provided order ID',
    response_description='The deleted order details',
    responses={
        200: {
            'description': 'The deleted order',
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
def handle_delete_order(delete_input: Annotated[DeleteOrderRequest, Body(embed=False, media_type='application/json')]) -> DeleteOrderOutput:
    env_vars: MyHandlerEnvVars = get_environment_variables(model=MyHandlerEnvVars)
    logger.debug('environment variables', env_vars=env_vars.model_dump())
    logger.info('got delete order request', order_id=delete_input.order_id)

    metrics.add_metric(name='ValidDeleteOrderEvents', unit=MetricUnit.Count, value=1)
    response: DeleteOrderOutput = delete_order(
        delete_request=delete_input,
        table_name=env_vars.TABLE_NAME,
        context=app.lambda_context,
    )

    logger.info('finished handling delete order request')
    return response


@app.exception_handler(OrderNotFoundException)
def handle_order_not_found_error(ex: OrderNotFoundException):
    logger.exception('order not found')
    return Response(
        status_code=HTTPStatus.NOT_FOUND, content_type=content_types.APPLICATION_JSON, body=OrderNotFoundOutput().model_dump()
    )


@init_environment_variables(model=MyHandlerEnvVars)
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@metrics.log_metrics
@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    return app.resolve(event, context)