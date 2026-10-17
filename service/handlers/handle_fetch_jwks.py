from typing import Any

from service.logic.jwks import fetch_jwks

JWKS_ATTRIBUTE = 'Jwks'


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """CloudFormation custom resource (CDK provider framework) that returns the user pool JWKS as the 'Jwks' attribute.

    Lambda functions without internet access (the managed instances list Lambda) can't download the JWKS at runtime:
    the Cognito VPC endpoint serves only the user pool API, not the '.well-known/jwks.json' document.
    The keys are fetched once at deploy time and handed to those functions as an environment variable instead.

    This function is deployed without the common layer, so it must not import third party packages.
    """
    user_pool_id: str = event['ResourceProperties']['UserPoolId']
    if event['RequestType'] == 'Delete':
        return {'PhysicalResourceId': event['PhysicalResourceId']}
    return {'PhysicalResourceId': user_pool_id, 'Data': {JWKS_ATTRIBUTE: fetch_jwks(user_pool_id)}}
