import json
from http import HTTPStatus
from typing import Any, Dict

from aws_lambda_powertools.utilities.typing import LambdaContext

from service.handlers.schemas.env_vars import MyHandlerEnvVars
from service.handlers.utils.env_vars_parser import get_environment_variables, init_environment_variables


@init_environment_variables(model=MyHandlerEnvVars)
def my_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    env_vars: MyHandlerEnvVars = get_environment_variables(model=MyHandlerEnvVars)  # noqa: F841
    return {'statusCode': HTTPStatus.OK, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'message': 'success'})}
