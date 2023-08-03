from http import HTTPStatus
from typing import Any, Dict

from aws_lambda_env_modeler import get_environment_variables, init_environment_variables
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.feature_flags.exceptions import ConfigurationStoreError, SchemaValidationError
from aws_lambda_powertools.utilities.idempotency import idempotent
from aws_lambda_powertools.utilities.parser import ValidationError, parse
from aws_lambda_powertools.utilities.parser.envelopes import ApiGatewayEnvelope
from aws_lambda_powertools.utilities.typing import LambdaContext

from service.handlers.schemas.dynamic_configuration import MyConfiguration
from service.handlers.schemas.env_vars import MyHandlerEnvVars
from service.handlers.utils.dynamic_configuration import parse_configuration
from service.handlers.utils.http_responses import build_response
from service.handlers.utils.idempotency import IDEMPOTENCY_CONFIG, IDEMPOTENCY_LAYER
from service.handlers.utils.observability import logger, metrics, tracer
from service.logic.handle_create_request import handle_create_request
from service.schemas.exceptions import InternalServerException
from service.schemas.input import CreateOrderRequest
from service.schemas.output import CreateOrderOutput


@init_environment_variables(model=MyHandlerEnvVars)
@metrics.log_metrics
@idempotent(persistence_store=IDEMPOTENCY_LAYER, config=IDEMPOTENCY_CONFIG)
@tracer.capture_lambda_handler(capture_response=False)
def create_order(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    logger.set_correlation_id(context.aws_request_id)

    env_vars: MyHandlerEnvVars = get_environment_variables(model=MyHandlerEnvVars)
    logger.debug('environment variables', extra=env_vars.model_dump())

    try:
        my_configuration: MyConfiguration = parse_configuration(model=MyConfiguration)  # type: ignore
        logger.debug('fetched dynamic configuration', extra={'configuration': my_configuration.model_dump()})
    except (SchemaValidationError, ConfigurationStoreError) as exc:
        logger.exception(f'dynamic configuration error, error={str(exc)}')
        return build_response(http_status=HTTPStatus.INTERNAL_SERVER_ERROR, body={})

    try:
        # we want to extract and parse the HTTP body from the api gw envelope
        create_input: CreateOrderRequest = parse(event=event, model=CreateOrderRequest, envelope=ApiGatewayEnvelope)
        logger.info('got create order request', extra={'order_item_count': create_input.order_item_count})
    except (ValidationError, TypeError) as exc:  # pragma: no cover
        logger.error('event failed input validation', extra={'error': str(exc)})
        return build_response(http_status=HTTPStatus.BAD_REQUEST, body={})

    metrics.add_metric(name='ValidCreateOrderEvents', unit=MetricUnit.Count, value=1)
    try:
        response: CreateOrderOutput = handle_create_request(
            order_request=create_input,
            table_name=env_vars.TABLE_NAME,
        )
    except InternalServerException:  # pragma: no cover
        logger.error('finished handling create order request with internal error')
        return build_response(http_status=HTTPStatus.INTERNAL_SERVER_ERROR, body={})

    logger.info('finished handling create order request')
    return build_response(http_status=HTTPStatus.OK, body=response.model_dump())
