from aws_lambda_powertools.logging.logger import Logger
from aws_lambda_powertools.tracing.tracer import Tracer

SERVICE_NAME = 'my_service'

# JSON output format, service name can be set by environment variable "POWERTOOLS_SERVICE_NAME"
logger: Logger = Logger()

# service name can be set by environment variable "POWERTOOLS_SERVICE_NAME". Disabled by setting POWERTOOLS_TRACE_DISABLED to "True"
tracer: Tracer = Tracer()
