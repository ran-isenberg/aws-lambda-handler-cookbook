import json
from http import HTTPStatus
from typing import Any

from aws_lambda_env_modeler import get_environment_variables, init_environment_variables
from aws_lambda_powertools.utilities.typing import LambdaContext

from service.handlers.models.env_vars import MyHandlerEnvVars


@init_environment_variables(model=MyHandlerEnvVars)
def my_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    env_vars: MyHandlerEnvVars = get_environment_variables(model=MyHandlerEnvVars)  # noqa: F841
    return {'statusCode': HTTPStatus.OK, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'message': 'success'})}
