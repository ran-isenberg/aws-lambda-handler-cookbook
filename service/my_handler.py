from http import HTTPStatus
from typing import Any, Dict

from aws_lambda_context import LambdaContext
from aws_lambda_powertools import Logger


def my_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    logger = Logger('my_service')  # JSON output format
    logger.set_correlation_id(context.aws_request_id)
    logger.debug('my_handler is called')
    return {'statusCode': HTTPStatus.OK, 'headers': {'Content-Type': 'application/json'}, 'body': {}}
