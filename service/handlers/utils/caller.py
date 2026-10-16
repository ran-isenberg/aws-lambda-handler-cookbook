from service.handlers.utils.rest_api_resolver import app
from service.models.exceptions import InternalServerException


def get_caller_id() -> str:
    """The verified caller's user id: the access token 'sub' claim, which identifies the owner of an order.

    Call it only from a route protected by REQUIRE_READ or REQUIRE_WRITE (see auth.py), their middleware adds the verified claims to the
    resolver context. 'sub' is immutable and unique per user pool user, unlike the username which can be reused after a user is deleted.
    Kept out of auth.py, which builds the verifier from environment variables at import time.
    """
    caller_id = (app.context.get('claims') or {}).get('sub')
    if not isinstance(caller_id, str) or not caller_id:
        raise InternalServerException('verified access token claims with a sub claim are missing')
    return caller_id
