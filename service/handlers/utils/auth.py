from collections.abc import Callable
from typing import Any

from aws_lambda_env_modeler import get_environment_variables
from aws_lambda_powertools.event_handler.openapi.types import OpenAPIResponse
from aws_lambda_powertools.utilities.auth_alpha import JWTVerifier

from service.handlers.models.env_vars import Authentication
from service.handlers.utils.rest_api_resolver import BEARER_SECURITY_SCHEME_NAME, app
from service.logic.token_scopes import READ_SCOPE, WRITE_SCOPE
from service.models.exceptions import InternalServerException
from service.models.output import ForbiddenOutput, UnauthorizedOutput

_env_vars: Authentication = get_environment_variables(model=Authentication)

# Created once per execution environment, so the cached JWKS is reused across warm invocations.
# The pre token generation trigger adds the app client id as the 'aud' claim (see cdk/service/auth_construct.py),
# which is what the Cognito profile of the verifier validates as the resource audience.
# When COGNITO_JWKS is set (functions without internet access), the verifier uses those keys and never fetches the JWKS URL.
verifier: JWTVerifier = JWTVerifier.cognito(
    user_pool_id=_env_vars.COGNITO_USER_POOL_ID,
    client_id=_env_vars.COGNITO_CLIENT_ID,
    audience=_env_vars.COGNITO_CLIENT_ID,
    jwks=_env_vars.COGNITO_JWKS,
)

# Route middlewares: 401 for a missing/invalid token, 403 for a missing scope. Pass as `middlewares=` to a route.
REQUIRE_READ: list[Callable[..., Any]] = [verifier.require(scopes=[READ_SCOPE])]
REQUIRE_WRITE: list[Callable[..., Any]] = [verifier.require(scopes=[WRITE_SCOPE])]


def get_caller_id() -> str:
    """The verified caller's user id: the access token 'sub' claim, which identifies the owner of an order.

    Call it only from a route protected by REQUIRE_READ or REQUIRE_WRITE, their middleware adds the verified claims to the resolver context.
    'sub' is immutable and unique per user pool user, unlike the username which can be reused after a user is deleted.
    """
    caller_id = (app.context.get('claims') or {}).get('sub')
    if not isinstance(caller_id, str) or not caller_id:
        raise InternalServerException('verified access token claims with a sub claim are missing')
    return caller_id


# OpenAPI: the security requirement and the auth failure responses to document on a protected route.
BEARER_SECURITY: list[dict[str, list[str]]] = [{BEARER_SECURITY_SCHEME_NAME: []}]
AUTH_RESPONSES: dict[int, OpenAPIResponse] = {
    401: {
        'description': 'Missing or invalid access token',
        'content': {'application/json': {'model': UnauthorizedOutput}},
    },
    403: {
        'description': 'The access token does not have the required scope',
        'content': {'application/json': {'model': ForbiddenOutput}},
    },
}
