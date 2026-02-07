import json
from http import HTTPStatus
from typing import Any

from aws_lambda_powertools.tracing.tracer import Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

SERVICE_NAME = 'service'

# service name can be set by environment variable "POWERTOOLS_SERVICE_NAME". Disabled by setting POWERTOOLS_TRACE_DISABLED to "True"
tracer: Tracer = Tracer(service=SERVICE_NAME)


@tracer.capture_method(capture_response=False)
def inner_function_example(event: dict[str, Any]) -> dict[str, Any]:
    return {}


@tracer.capture_lambda_handler(capture_response=False)
def my_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    inner_function_example(event)
    return {'statusCode': HTTPStatus.OK, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'message': 'success'})}
