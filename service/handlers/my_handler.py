import json
from http import HTTPStatus
from typing import Any, Dict

from aws_lambda_powertools.utilities.typing import LambdaContext

from service.utils.infra import logger, tracer


@tracer.capture_method(capture_response=False)
def inner_function_example(event: Dict[str, Any]) -> Dict[str, Any]:
    return {}


def new_func_not_called_cov_check() -> None:
    return


@tracer.capture_lambda_handler(capture_response=False)
def my_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    logger.set_correlation_id(context.aws_request_id)
    logger.debug('my_handler is called, calling inner_function_example')
    inner_function_example(event)
    logger.debug('inner_function_example finished successfully')
    return {'statusCode': HTTPStatus.OK, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'message': 'success'})}
