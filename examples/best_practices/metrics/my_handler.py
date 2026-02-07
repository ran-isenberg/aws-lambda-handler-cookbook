import json
from http import HTTPStatus
from typing import Any

from aws_lambda_powertools.metrics import Metrics, MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext

SERVICE_NAME = 'service'

# namespace and service name can be set by environment variable "POWERTOOLS_METRICS_NAMESPACE" and "POWERTOOLS_SERVICE_NAME" accordingly
metrics = Metrics(namespace='my_product_kpi', service=SERVICE_NAME)


@metrics.log_metrics
def my_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    metrics.add_metric(name='ValidEvents', unit=MetricUnit.Count, value=1)
    return {'statusCode': HTTPStatus.OK, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'message': 'success'})}
