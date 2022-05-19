from http import HTTPStatus
from typing import Any, Dict

from aws_lambda_powertools.metrics.metrics import MetricUnit
from aws_lambda_powertools.utilities.feature_flags.exceptions import ConfigurationStoreError, SchemaValidationError
from aws_lambda_powertools.utilities.parser import ValidationError, parse
from aws_lambda_powertools.utilities.parser.envelopes import ApiGatewayEnvelope
from aws_lambda_powertools.utilities.typing import LambdaContext

from service.handlers.schemas.dynamic_configuration import FeatureFlagsNames, MyConfiguration
from service.handlers.schemas.env_vars import MyHandlerEnvVars
from service.handlers.schemas.input import Input
from service.handlers.schemas.output import Output
from service.handlers.utils.dynamic_configuration import get_dynamic_configuration_store, parse_configuration
from service.handlers.utils.env_vars_parser import get_environment_variables, init_environment_variables
from service.handlers.utils.http_responses import build_response
from service.handlers.utils.observability import logger, metrics, tracer


@tracer.capture_method(capture_response=False)
def inner_function_example(my_name: str, order_item_count: int) -> Output:
    # process input, etc. return output
    config_store = get_dynamic_configuration_store()
    campaign: bool = config_store.evaluate(
        name=FeatureFlagsNames.TEN_PERCENT_CAMPAIGN.value,
        context={},
        default=False,
    )
    logger.debug('campaign feature flag value', extra={'campaign': campaign})
    premium: bool = config_store.evaluate(
        name=FeatureFlagsNames.PREMIUM.value,
        context={'customer_name': my_name},
        default=False,
    )
    logger.debug('premium feature flag value', extra={'premium': premium})
    return Output(success=True, order_item_count=order_item_count)


@init_environment_variables(model=MyHandlerEnvVars)
@metrics.log_metrics
@tracer.capture_lambda_handler(capture_response=False)
def my_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    logger.set_correlation_id(context.aws_request_id)
    logger.info('my_handler is called, calling inner_function_example')

    env_vars: MyHandlerEnvVars = get_environment_variables(model=MyHandlerEnvVars)
    logger.debug('environment variables', extra=env_vars.dict())

    try:
        my_configuration: MyConfiguration = parse_configuration(model=MyConfiguration)
        logger.debug('fetched dynamic configuration', extra={'configuration': my_configuration.dict()})
    except (SchemaValidationError, ConfigurationStoreError) as exc:
        logger.exception(f'dynamic configuration error, error={str(exc)}')
        return build_response(http_status=HTTPStatus.INTERNAL_SERVER_ERROR, body={})

    try:
        # we want to extract and parse the HTTP body from the api gw envelope
        input: Input = parse(event=event, model=Input, envelope=ApiGatewayEnvelope)
        logger.info('got create request', extra={'order_item_count': input.order_item_count})
    except (ValidationError, TypeError) as exc:
        logger.error('event failed input validation', extra={'error': str(exc)})
        return build_response(http_status=HTTPStatus.BAD_REQUEST, body={})

    response: Output = inner_function_example(input.my_name, input.order_item_count)
    logger.info('inner_function_example finished successfully')
    metrics.add_metric(name='ValidEvents', unit=MetricUnit.Count, value=1)
    return build_response(http_status=HTTPStatus.OK, body=response.dict())
