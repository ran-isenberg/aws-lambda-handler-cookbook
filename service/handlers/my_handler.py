import json
from http import HTTPStatus
from typing import Any, Dict

from aws_lambda_powertools.metrics.metrics import MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext

from service.handlers.schemas.env_vars import MyHandlerEnvVars
from service.handlers.utils.env_vars_parser import get_environment_variables, init_environment_variables
from service.handlers.utils.observability import logger, metrics, tracer


@tracer.capture_method(capture_response=False)
def inner_function_example(event: Dict[str, Any]) -> Dict[str, Any]:
    return {}


@init_environment_variables(model=MyHandlerEnvVars)
@metrics.log_metrics
@tracer.capture_lambda_handler(capture_response=False)
def my_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    logger.set_correlation_id(context.aws_request_id)
    logger.info('my_handler is called, calling inner_function_example')

    env_vars: MyHandlerEnvVars = get_environment_variables()
    logger.debug('environment variables', extra=env_vars.dict())

    inner_function_example(event)
    logger.info('inner_function_example finished successfully')
    metrics.add_metric(name='ValidEvents', unit=MetricUnit.Count, value=1)
    return {'statusCode': HTTPStatus.OK, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'message': 'success'})}
