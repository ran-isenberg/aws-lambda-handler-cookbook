import json
from http import HTTPStatus
from typing import Any, Dict

from aws_lambda_powertools.logging.logger import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

logger: Logger = Logger(service='my_service')  # JSON output format, service name can be set by environment variable "POWERTOOLS_SERVICE_NAME"


def my_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    logger.set_correlation_id(context.aws_request_id)
    logger.debug('my_handler is called')
    return {'statusCode': HTTPStatus.OK, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'message': 'success'})}
