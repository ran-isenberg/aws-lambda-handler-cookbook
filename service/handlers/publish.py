from __future__ import annotations

from typing import Any

from aws_lambda_env_modeler import init_environment_variables
from aws_lambda_powertools.event_handler import AppSyncEventsResolver
from aws_lambda_powertools.event_handler.events_appsync.exceptions import UnauthorizedException
from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.metrics import Metrics, MetricUnit
from aws_lambda_powertools.tracing import Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

from service.handlers.models.env_vars import MyHandleVars

METRICS_NAMESPACE = 'appsync_events_kpi'

# JSON output format, service name can be set by environment variable "POWERTOOLS_SERVICE_NAME"
logger: Logger = Logger()

# service name can be set by environment variable "POWERTOOLS_SERVICE_NAME". Disabled by setting POWERTOOLS_TRACE_DISABLED to "True"
tracer: Tracer = Tracer()

# namespace and service name can be set by environment variable "POWERTOOLS_METRICS_NAMESPACE" and "POWERTOOLS_SERVICE_NAME" accordingly
metrics = Metrics(namespace=METRICS_NAMESPACE)

app = AppSyncEventsResolver()


class ValidationError(Exception):
    pass


@app.on_publish('/default/channel1')
def handle_specific_channel(payload: dict[str, Any]):
    # This handler will be called for events on /default/channel1
    logger.info('specific_channel_handler')

    # do input validation here with Pydantic or similar
    # if not is_valid_payload:
    # raise ValidationError('Invalid payload format')

    # Perform any necessary processing on the payload
    logger.info('payload_processing', payload=payload)
    # For example, you could modify the payload or log it

    return {
        'processed': True,
        'original_payload': payload,
    }


@app.on_publish('/default/*')
def handle_default_namespace(payload: dict[str, Any]):
    # This handler will be called for all channels in the default namespace
    # EXCEPT for /default/channel1 which has a more specific handler

    logger.info('default_namespace_handler')

    # do input validation here with Pydantic or similar
    # if not is_valid_payload:
    # raise ValidationError('Invalid payload format')

    # Perform any necessary processing on the payload
    logger.info('payload_processing')
    # For example, you could modify the payload or log it

    return {
        'processed': True,
        'original_payload': payload,
    }


@app.on_publish('/*')
def handle_all_channels(payload: dict[str, Any]):
    # This handler will be called for all channels in all namespaces
    # EXCEPT for those that have more specific handlers
    logger.info('catch_all_handler', payload=payload)

    # do input validation here with Pydantic or similar
    # if not is_valid_payload:
    # raise ValidationError('Invalid payload format')

    # Perform any necessary processing on the payload
    logger.info('payload_processing', payload=payload)
    # For example, you could modify the payload or log it

    return {
        'processed': True,
        'original_payload': payload,
    }


@app.on_subscribe('/*')
def handle_all_subscriptions():
    path = app.current_event.info.channel_path

    # Perform access control checks
    if not is_authorized(path):
        raise UnauthorizedException('You are not authorized to subscribe to this channel')

    metrics.add_dimension(name='channel', value=path)
    metrics.add_metric(name='subscription', unit=MetricUnit.Count, value=1)

    return True


def is_authorized(path: str):
    return True  # Replace with your authorization logic


@init_environment_variables(model=MyHandleVars)
@logger.inject_lambda_context()
@metrics.log_metrics
@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    return app.resolve(event, context)
