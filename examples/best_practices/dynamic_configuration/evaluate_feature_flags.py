import json
from http import HTTPStatus
from typing import Any

from aws_lambda_env_modeler import init_environment_variables
from aws_lambda_powertools.utilities.typing import LambdaContext

from service.handlers.models.dynamic_configuration import MyConfiguration
from service.handlers.models.env_vars import MyHandlerEnvVars
from service.handlers.utils.dynamic_configuration import get_configuration_store, parse_configuration
from service.handlers.utils.observability import logger


@init_environment_variables(model=MyHandlerEnvVars)
def my_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    try:
        my_configuration: MyConfiguration = parse_configuration(model=MyConfiguration)  # type: ignore
        logger.debug('fetched dynamic configuration', configuration=my_configuration.model_dump())
    except Exception:
        logger.exception('dynamic configuration error')
        return {'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'headers': {'Content-Type': 'application/json'}, 'body': ''}

    campaign = get_configuration_store().evaluate(
        name='ten_percent_off_campaign',
        context={},
        default=False,
    )
    logger.debug('campaign feature flag value', campaign=campaign)

    premium = get_configuration_store().evaluate(
        name='premium_features',
        context={'customer_name': 'RanTheBuilder'},
        default=False,
    )
    logger.debug('premium feature flag value', premium=premium)
    return {'statusCode': HTTPStatus.OK, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'message': 'success'})}
