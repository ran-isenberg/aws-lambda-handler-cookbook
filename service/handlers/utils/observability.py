from aws_lambda_powertools.logging.logger import Logger
from aws_lambda_powertools.metrics.metrics import Metrics
from aws_lambda_powertools.tracing.tracer import Tracer

METRICS_NAMESPACE = 'orders_kpi'

# JSON output format, service name can be set by environment variable "POWERTOOLS_SERVICE_NAME"
logger: Logger = Logger()

# service name can be set by environment variable "POWERTOOLS_SERVICE_NAME". Disabled by setting POWERTOOLS_TRACE_DISABLED to "True"
tracer: Tracer = Tracer()

# namespace and service name can be set by environment variable "POWERTOOLS_METRICS_NAMESPACE" and "POWERTOOLS_SERVICE_NAME" accordingly
metrics = Metrics(namespace=METRICS_NAMESPACE)
