from aws_cdk import App
from aws_cdk.assertions import Match, Template

from cdk.service.constants import MANAGERS_GROUP, USER_POOL_CLIENT_ID_OUTPUT, USER_POOL_ID_OUTPUT
from cdk.service.service_stack import ServiceStack


def test_synthesizes_properly():
    app = App()

    service_stack = ServiceStack(app, 'service-test', is_production_env=True)

    # Prepare the stack for assertions.
    template = Template.from_stack(service_stack)

    # verify that we have one API GW, that is it not deleted by mistake
    template.resource_count_is('AWS::ApiGateway::RestApi', 1)
    template.resource_count_is('AWS::DynamoDB::GlobalTable', 2)  # main db and one for idempotency


def test_cognito_user_pool():
    app = App()

    service_stack = ServiceStack(app, 'service-test', is_production_env=True)
    template = Template.from_stack(service_stack)

    # one user pool on the Essentials plan (required for access token customization) with admin-only user creation
    template.resource_count_is('AWS::Cognito::UserPool', 1)
    template.has_resource_properties(
        'AWS::Cognito::UserPool',
        {
            'UserPoolTier': 'ESSENTIALS',
            'AdminCreateUserConfig': {'AllowAdminCreateUserOnly': True},
            # pre token generation V2 adds the aud claim and the scopes to access tokens
            'LambdaConfig': {'PreTokenGenerationConfig': {'LambdaVersion': 'V2_0', 'LambdaArn': Match.any_value()}},
        },
    )

    # one app client that can sign in through the admin API (used by the tests to mint real tokens), without a secret
    template.resource_count_is('AWS::Cognito::UserPoolClient', 1)
    template.has_resource_properties(
        'AWS::Cognito::UserPoolClient',
        {'GenerateSecret': False, 'ExplicitAuthFlows': ['ALLOW_ADMIN_USER_PASSWORD_AUTH', 'ALLOW_REFRESH_TOKEN_AUTH']},
    )

    # the only group: its members get the manage scope (create and delete orders)
    template.resource_count_is('AWS::Cognito::UserPoolGroup', 1)
    template.has_resource_properties('AWS::Cognito::UserPoolGroup', {'GroupName': MANAGERS_GROUP})

    # the tests read the pool details from the stack outputs
    template.has_output(USER_POOL_ID_OUTPUT, {})
    template.has_output(USER_POOL_CLIENT_ID_OUTPUT, {})


def test_order_lambdas_get_cognito_env_vars():
    app = App()

    service_stack = ServiceStack(app, 'service-test', is_production_env=True)
    template = Template.from_stack(service_stack)

    # create, get, delete and list verify access tokens, so each one needs the pool details
    order_lambdas = template.find_resources(
        'AWS::Lambda::Function',
        {'Properties': {'Environment': {'Variables': {'COGNITO_USER_POOL_ID': Match.any_value(), 'COGNITO_CLIENT_ID': Match.any_value()}}}},
    )
    assert len(order_lambdas) == 4


def test_managed_instances_list_lambda_gets_jwks_at_deploy_time():
    app = App()

    service_stack = ServiceStack(app, 'service-test', is_production_env=True)
    template = Template.from_stack(service_stack)

    # the Cognito VPC endpoint serves only the user pool API, not the JWKS document, so the list Lambda (no internet access)
    # gets the user pool public keys as an env var, fetched at deploy time by a custom resource that runs outside the VPC
    template.resource_count_is('AWS::CloudFormation::CustomResource', 1)
    template.has_resource_properties('AWS::CloudFormation::CustomResource', {'UserPoolId': Match.any_value()})
    jwks_lambdas = template.find_resources(
        'AWS::Lambda::Function',
        {
            'Properties': {
                'Environment': {'Variables': {'COGNITO_JWKS': {'Fn::GetAtt': [Match.any_value(), 'Jwks']}}},
                'CapacityProviderConfig': Match.any_value(),
            }
        },
    )
    assert len(jwks_lambdas) == 1
    vpc_endpoints = template.find_resources('AWS::EC2::VPCEndpoint')
    assert not [endpoint for endpoint in vpc_endpoints.values() if 'cognito-idp' in str(endpoint['Properties']['ServiceName'])]


def test_orders_are_partitioned_by_owner():
    app = App()

    service_stack = ServiceStack(app, 'service-test', is_production_env=True)
    template = Template.from_stack(service_stack)

    # users only reach their own orders: the orders table is keyed by (owner_id, id)
    template.has_resource_properties(
        'AWS::DynamoDB::GlobalTable',
        {
            'KeySchema': [{'AttributeName': 'owner_id', 'KeyType': 'HASH'}, {'AttributeName': 'id', 'KeyType': 'RANGE'}],
        },
    )

    # the list Lambda queries the caller's partition, it never scans the whole table
    policies = template.find_resources('AWS::IAM::Role', {'Properties': {'Policies': Match.any_value()}})
    actions = str([role['Properties']['Policies'] for role in policies.values()])
    assert 'dynamodb:Query' in actions
    assert 'dynamodb:Scan' not in actions
