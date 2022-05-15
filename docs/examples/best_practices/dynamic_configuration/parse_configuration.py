from http import HTTPStatus
from typing import Any, Dict

from aws_lambda_powertools.utilities.feature_flags.exceptions import ConfigurationStoreError, SchemaValidationError
from aws_lambda_powertools.utilities.typing import LambdaContext

from service.handlers.schemas.dynamic_configuration import MyConfiguration
from service.handlers.schemas.env_vars import MyHandlerEnvVars
from service.handlers.utils.dynamic_configuration import parse_configuration
from service.handlers.utils.env_vars_parser import init_environment_variables
from service.handlers.utils.http_responses import build_response
from service.handlers.utils.observability import logger


@init_environment_variables(model=MyHandlerEnvVars)
def my_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    try:
        my_configuration: MyConfiguration = parse_configuration(model=MyConfiguration)
    except (SchemaValidationError, ConfigurationStoreError) as exc:
        logger.exception(f'dynamic configuration error, error={str(exc)}')
        return build_response(http_status=HTTPStatus.INTERNAL_SERVER_ERROR, body={})

    logger.debug('fetched dynamic configuration', extra={'countries': my_configuration.countries})
    return build_response(http_status=HTTPStatus.OK, body={'message': 'success'})
