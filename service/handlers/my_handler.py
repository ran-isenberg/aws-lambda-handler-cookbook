from http import HTTPStatus
from typing import Any, Dict

from aws_lambda_powertools.metrics.metrics import MetricUnit
from aws_lambda_powertools.utilities.parser import ValidationError, parse
from aws_lambda_powertools.utilities.parser.envelopes import ApiGatewayEnvelope
from aws_lambda_powertools.utilities.typing import LambdaContext

from service.handlers.schemas.dynamic_configuration import FeatureFlagsNames, MyConfiguration
from service.handlers.schemas.env_vars import MyHandlerEnvVars
from service.handlers.schemas.input import Input
from service.handlers.utils.dynamic_configuration import get_dynamic_configuration, parse_configuration
from service.handlers.utils.env_vars_parser import get_environment_variables, init_environment_variables
from service.handlers.utils.http_responses import build_response
from service.handlers.utils.observability import logger, metrics, tracer


@tracer.capture_method(capture_response=False)
def inner_function_example(my_name: str, order_item_count: int) -> Dict[str, Any]:
    # process input, etc. return output
    my_feature: bool = get_dynamic_configuration().evaluate(
        name=FeatureFlagsNames.TEN_PERCENT_CAMPAIGN.value,
        context={},
        default=False,
    )
    logger.debug('campaign feature flag value', extra={'campaign': my_feature})
    return {}


@init_environment_variables(model=MyHandlerEnvVars)
@metrics.log_metrics
@tracer.capture_lambda_handler(capture_response=False)
def my_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    logger.set_correlation_id(context.aws_request_id)
    logger.info('my_handler is called, calling inner_function_example')

    env_vars: MyHandlerEnvVars = get_environment_variables(model=MyHandlerEnvVars)
    logger.debug('environment variables', extra=env_vars.dict())

    my_configuration: MyConfiguration = parse_configuration(model=MyConfiguration)
    logger.debug('fetched dynamic configuration', extra={'configuration': my_configuration.dict()})

    # my_feature_flag: bbb

    try:
        # we want to extract and parse the HTTP body from the api gw envelope
        input: Input = parse(event=event, model=Input, envelope=ApiGatewayEnvelope)
        logger.info('got create request', extra={'order_item_count': input.order_item_count})
    except (ValidationError, TypeError) as exc:
        logger.error('event failed input validation', extra={'error': str(exc)})
        return build_response(http_status=HTTPStatus.BAD_REQUEST, body={})

    inner_function_example(input.my_name, input.order_item_count)
    logger.info('inner_function_example finished successfully')
    metrics.add_metric(name='ValidEvents', unit=MetricUnit.Count, value=1)
    return build_response(http_status=HTTPStatus.OK, body={'message': 'success'})
