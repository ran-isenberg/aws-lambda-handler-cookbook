import json
import urllib.request
from typing import Any

FETCH_TIMEOUT_SECONDS = 5


def jwks_url(user_pool_id: str) -> str:
    """The public URL of the user pool token signing keys (JWKS)."""
    region = user_pool_id.split('_', 1)[0]
    domain = 'amazonaws.com.cn' if region.startswith('cn-') else 'amazonaws.com'
    return f'https://cognito-idp.{region}.{domain}/{user_pool_id}/.well-known/jwks.json'


def fetch_jwks(user_pool_id: str) -> str:
    """Download the user pool JWKS and return it as a compact JSON string.

    Raises ValueError when the response is not a JWKS (an object with a 'keys' array).
    """
    with urllib.request.urlopen(jwks_url(user_pool_id), timeout=FETCH_TIMEOUT_SECONDS) as response:  # noqa: S310 - fixed https URL
        jwks: Any = json.loads(response.read())
    if not isinstance(jwks, dict) or not isinstance(jwks.get('keys'), list) or not jwks['keys']:
        raise ValueError('response is not a JWKS')
    return json.dumps(jwks, separators=(',', ':'))
