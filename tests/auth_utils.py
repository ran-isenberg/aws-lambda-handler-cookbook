import secrets
import uuid
from dataclasses import dataclass
from functools import lru_cache

import boto3

from cdk.service.constants import USER_POOL_CLIENT_ID_OUTPUT, USER_POOL_ID_OUTPUT
from tests.utils import generate_random_string, get_stack_output


@dataclass(frozen=True)
class CognitoPool:
    user_pool_id: str
    client_id: str


@dataclass(frozen=True)
class CognitoUser:
    username: str
    access_token: str
    id_token: str


def bearer_headers(access_token: str) -> dict[str, str]:
    return {'Authorization': f'Bearer {access_token}'}


def get_cognito_pool() -> CognitoPool:
    """The deployed user pool and app client, read from the stack outputs."""
    return CognitoPool(user_pool_id=get_stack_output(USER_POOL_ID_OUTPUT), client_id=get_stack_output(USER_POOL_CLIENT_ID_OUTPUT))


@lru_cache
def _cognito_client(user_pool_id: str):
    # the region is the prefix of the user pool id (us-east-1_xxx), so it does not depend on the local AWS configuration
    return boto3.client('cognito-idp', region_name=user_pool_id.split('_')[0])


def create_cognito_user(pool: CognitoPool, groups: list[str]) -> CognitoUser:
    """Create a user in the given groups and sign it in with the Cognito API to get real tokens.

    Delete it with delete_cognito_user.
    """
    client = _cognito_client(pool.user_pool_id)
    username = f'test-{generate_random_string(10)}-{uuid.uuid4().hex[:8]}'
    password = f'Aa1!{secrets.token_urlsafe(16)}'  # meets the user pool password policy
    client.admin_create_user(UserPoolId=pool.user_pool_id, Username=username, MessageAction='SUPPRESS')  # SUPPRESS: no invitation message
    try:
        client.admin_set_user_password(UserPoolId=pool.user_pool_id, Username=username, Password=password, Permanent=True)
        for group in groups:
            client.admin_add_user_to_group(UserPoolId=pool.user_pool_id, Username=username, GroupName=group)
        auth_result = client.admin_initiate_auth(
            UserPoolId=pool.user_pool_id,
            ClientId=pool.client_id,
            AuthFlow='ADMIN_USER_PASSWORD_AUTH',
            AuthParameters={'USERNAME': username, 'PASSWORD': password},
        )['AuthenticationResult']
    except Exception:
        # do not leave a half created user behind, the caller never gets the chance to delete it
        delete_cognito_user(pool, username)
        raise
    return CognitoUser(username=username, access_token=auth_result['AccessToken'], id_token=auth_result['IdToken'])


def delete_cognito_user(pool: CognitoPool, username: str) -> None:
    client = _cognito_client(pool.user_pool_id)
    try:
        client.admin_delete_user(UserPoolId=pool.user_pool_id, Username=username)
    except client.exceptions.UserNotFoundException:
        pass
