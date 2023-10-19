import json
from http import HTTPStatus
from typing import Any

from aws_lambda_env_modeler import init_environment_variables
from aws_lambda_powertools.utilities.typing import LambdaContext

from service.handlers.models.dynamic_configuration import MyConfiguration
from service.handlers.models.env_vars import MyHandlerEnvVars
from service.handlers.utils.dynamic_configuration import parse_configuration
from service.handlers.utils.observability import logger


def build_response(http_status: HTTPStatus, body: dict[str, Any]) -> dict[str, Any]:
    return {'statusCode': http_status, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps(body)}


@init_environment_variables(model=MyHandlerEnvVars)
def my_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    try:
        my_configuration = parse_configuration(model=MyConfiguration)
    except Exception:
        logger.exception('dynamic configuration error')
        return build_response(http_status=HTTPStatus.INTERNAL_SERVER_ERROR, body={})

    logger.debug('fetched dynamic configuration', countries=my_configuration.countries)
    return build_response(http_status=HTTPStatus.OK, body={'message': 'success'})
