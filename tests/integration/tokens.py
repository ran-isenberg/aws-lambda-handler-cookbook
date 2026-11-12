"""Cognito-shaped access and ID tokens, minted and signed locally for the integration tests.

The integration tests run against AWS Emulator, whose Cognito can't be used for this yet:
TODO: switch back to tokens issued by the emulator's Cognito once these aws/aws-emulator issues are fixed:
- the user pool JWKS has no RSA 'n'/'e', so its tokens can't be verified
  (issues/things-that-do-not-work/20261108T120220Z-cognito-idp-...-jwks-document-is.md)
- user pool Lambda triggers are not invoked, so tokens lack the 'aud' and scopes of the pre token generation trigger
  (issues/things-that-do-not-work/20261023T114649Z-cognito-idp-cognito-user-pool-lambda-triggers-are-not-invoked.md)

The handlers verify these tokens with their real JWTVerifier: its public key comes from the COGNITO_JWKS env var (as for
functions without internet access), and the 'aud' and scopes come from the real pre token generation trigger handler.
"""

import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa

from service.handlers.handle_pre_token_generation import lambda_handler as pre_token_generation_handler
from tests.auth_utils import CognitoPool, CognitoUser
from tests.utils import generate_context, generate_random_string

TEST_USER_POOL_ID = 'us-east-1_EMULATOR1'
TEST_CLIENT_ID = 'emulatortestclient0000000'
TOKEN_LIFETIME_SECONDS = 3600


@dataclass(frozen=True)
class TokenIssuer:
    """Plays the user pool: one RSA signing key per test session, published as a JWKS."""

    pool: CognitoPool = field(default_factory=lambda: CognitoPool(user_pool_id=TEST_USER_POOL_ID, client_id=TEST_CLIENT_ID))
    kid: str = field(default_factory=lambda: uuid.uuid4().hex)
    private_key: rsa.RSAPrivateKey = field(default_factory=lambda: rsa.generate_private_key(public_exponent=65537, key_size=2048))

    @property
    def issuer(self) -> str:
        region = self.pool.user_pool_id.split('_', 1)[0]
        return f'https://cognito-idp.{region}.amazonaws.com/{self.pool.user_pool_id}'

    def jwks(self) -> str:
        """The public JWKS (JSON string), as the COGNITO_JWKS env var of the handlers expects it."""
        public_jwk: dict[str, Any] = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(self.private_key.public_key()))
        public_jwk.update({'kid': self.kid, 'alg': 'RS256', 'use': 'sig'})
        return json.dumps({'keys': [public_jwk]})

    def _sign(self, claims: dict[str, Any]) -> str:
        return jwt.encode(claims, self.private_key, algorithm='RS256', headers={'kid': self.kid})

    def _access_token_overrides(self, groups: list[str]) -> dict[str, Any]:
        """Run the real pre token generation trigger, so its logic shapes the access token as on Cognito."""
        event = {
            'version': '2',
            'triggerSource': 'TokenGeneration_Authentication',
            'userPoolId': self.pool.user_pool_id,
            'callerContext': {'clientId': self.pool.client_id},
            'request': {'groupConfiguration': {'groupsToOverride': groups}, 'scopes': ['aws.cognito.signin.user.admin']},
            'response': {},
        }
        result = pre_token_generation_handler(event, generate_context())
        return result['response']['claimsAndScopeOverrideDetails']['accessTokenGeneration']

    def create_user(self, groups: list[str]) -> CognitoUser:
        """A signed in user of the given groups, with a Cognito-shaped access token and ID token."""
        username = f'test-{generate_random_string(10)}-{uuid.uuid4().hex[:8]}'
        sub = str(uuid.uuid4())
        now = int(time.time())
        common: dict[str, Any] = {'iss': self.issuer, 'sub': sub, 'iat': now, 'auth_time': now, 'exp': now + TOKEN_LIFETIME_SECONDS}
        if groups:
            common['cognito:groups'] = groups

        overrides = self._access_token_overrides(groups)
        scopes = ['aws.cognito.signin.user.admin', *overrides['scopesToAdd']]
        access_claims = {
            **common,
            'token_use': 'access',
            'client_id': self.pool.client_id,
            'username': username,
            'scope': ' '.join(scopes),
            'jti': str(uuid.uuid4()),
            **overrides['claimsToAddOrOverride'],
        }
        id_claims = {**common, 'token_use': 'id', 'aud': self.pool.client_id, 'cognito:username': username, 'jti': str(uuid.uuid4())}
        return CognitoUser(username=username, sub=sub, access_token=self._sign(access_claims), id_token=self._sign(id_claims))
