from typing import cast

from aws_cdk import Acknowledgment, CfnElement, CfnOutput, CustomResource, Duration, RemovalPolicy, Stack, Validations
from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_logs as logs
from aws_cdk import custom_resources as cr
from constructs import Construct

import cdk.service.constants as constants


class AuthConstruct(Construct):
    """Cognito user pool used to authenticate API callers.

    Access tokens are verified inside the order Lambdas with the Powertools ``JWTVerifier``.
    ``JWTVerifier.cognito()`` requires an ``aud`` claim, which Cognito only adds natively for Managed Login flows.
    A pre token generation (V2) trigger adds ``aud`` (the app client id) and scopes (derived from user pool groups)
    to access tokens issued by the Cognito API, so tests and backend clients can sign in without a browser.
    """

    LAMBDA_RUNTIME = _lambda.Runtime.PYTHON_3_14
    LAMBDA_ARCHITECTURE = _lambda.Architecture.ARM_64
    LAMBDA_LOGGING_FORMAT = _lambda.LoggingFormat.JSON

    def __init__(self, scope: Construct, id_: str) -> None:
        super().__init__(scope, id_)
        self.pre_token_func = self._build_pre_token_lambda()
        self.user_pool = self._build_user_pool(self.pre_token_func)
        self.user_pool_client = self._build_user_pool_client(self.user_pool)
        self._build_groups(self.user_pool)
        # the user pool public keys (JWKS) as a JSON string, for Lambdas without internet access (see handle_fetch_jwks)
        self.jwks = self._build_jwks_resource(self.user_pool)

        CfnOutput(self, id=constants.USER_POOL_ID_OUTPUT, value=self.user_pool.user_pool_id).override_logical_id(constants.USER_POOL_ID_OUTPUT)
        CfnOutput(self, id=constants.USER_POOL_CLIENT_ID_OUTPUT, value=self.user_pool_client.user_pool_client_id).override_logical_id(
            constants.USER_POOL_CLIENT_ID_OUTPUT
        )

    def _build_pre_token_lambda(self) -> _lambda.Function:
        log_group = logs.LogGroup(
            self,
            f'{constants.PRE_TOKEN_LAMBDA}LogGroup',
            retention=logs.RetentionDays.ONE_DAY,
            removal_policy=RemovalPolicy.DESTROY,
        )
        # pure python (no third party dependencies), so it does not need the common layer
        return _lambda.Function(
            self,
            constants.PRE_TOKEN_LAMBDA,
            runtime=self.LAMBDA_RUNTIME,
            code=_lambda.Code.from_asset(constants.BUILD_FOLDER),
            handler='service.handlers.handle_pre_token_generation.lambda_handler',
            tracing=_lambda.Tracing.ACTIVE,
            retry_attempts=0,
            timeout=Duration.seconds(constants.API_HANDLER_LAMBDA_TIMEOUT),
            memory_size=constants.API_HANDLER_LAMBDA_MEMORY_SIZE,
            log_group=log_group,
            logging_format=self.LAMBDA_LOGGING_FORMAT,
            system_log_level_v2=_lambda.SystemLogLevel.INFO,
            architecture=self.LAMBDA_ARCHITECTURE,
        )

    def _build_jwks_resource(self, user_pool: cognito.UserPool) -> str:
        log_group = logs.LogGroup(
            self,
            f'{constants.FETCH_JWKS_LAMBDA}LogGroup',
            retention=logs.RetentionDays.ONE_DAY,
            removal_policy=RemovalPolicy.DESTROY,
        )
        # runs outside any VPC, so it can download the JWKS from the public Cognito endpoint
        fetch_jwks_func = _lambda.Function(
            self,
            constants.FETCH_JWKS_LAMBDA,
            runtime=self.LAMBDA_RUNTIME,
            code=_lambda.Code.from_asset(constants.BUILD_FOLDER),
            handler='service.handlers.handle_fetch_jwks.lambda_handler',
            retry_attempts=0,
            timeout=Duration.seconds(constants.API_HANDLER_LAMBDA_TIMEOUT),
            memory_size=constants.API_HANDLER_LAMBDA_MEMORY_SIZE,
            log_group=log_group,
            logging_format=self.LAMBDA_LOGGING_FORMAT,
            system_log_level_v2=_lambda.SystemLogLevel.INFO,
            architecture=self.LAMBDA_ARCHITECTURE,
        )
        provider = cr.Provider(self, f'{constants.FETCH_JWKS_LAMBDA}Provider', on_event_handler=fetch_jwks_func)
        fetch_jwks_logical_id = Stack.of(self).get_logical_id(cast(CfnElement, fetch_jwks_func.node.default_child))
        Validations.of(provider).acknowledge(
            Acknowledgment(
                id=f'AwsSolutions-IAM5[Resource::<{fetch_jwks_logical_id}.Arn>:*]',
                reason='the CDK provider framework may invoke any version of the single JWKS fetch function it fronts',
            ),
        )
        # a new user pool id (pool replaced) triggers an update, which fetches the new pool's keys.
        # Cognito might rotate user pool signing keys (no published schedule). The keys are only refreshed on deploy,
        # so after a rotation the functions that use them reject new tokens until the next deployment.
        jwks_resource = CustomResource(
            self,
            constants.USER_POOL_JWKS_RESOURCE,
            service_token=provider.service_token,
            properties={'UserPoolId': user_pool.user_pool_id},
        )
        return jwks_resource.get_att_string('Jwks')

    def _build_user_pool(self, pre_token_func: _lambda.Function) -> cognito.UserPool:
        user_pool = cognito.UserPool(
            self,
            'UserPool',
            # access token customization (pre token generation V2) requires the Essentials (or Plus) feature plan
            feature_plan=cognito.FeaturePlan.ESSENTIALS,
            self_sign_up_enabled=False,  # users are provisioned by an admin only
            sign_in_aliases=cognito.SignInAliases(username=True),
            password_policy=cognito.PasswordPolicy(
                min_length=12,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=True,
            ),
            account_recovery=cognito.AccountRecovery.NONE,
            removal_policy=RemovalPolicy.DESTROY,
        )
        user_pool.add_trigger(
            cognito.UserPoolOperation.PRE_TOKEN_GENERATION_CONFIG,
            pre_token_func,
            lambda_version=cognito.LambdaVersion.V2_0,
        )
        return user_pool

    def _build_user_pool_client(self, user_pool: cognito.UserPool) -> cognito.UserPoolClient:
        return user_pool.add_client(
            'UserPoolClient',
            generate_secret=False,
            # server side (IAM authorized) sign in, used by the tests to mint real tokens
            auth_flows=cognito.AuthFlow(admin_user_password=True),
            prevent_user_existence_errors=True,
            access_token_validity=Duration.minutes(60),
            id_token_validity=Duration.minutes(60),
            enable_token_revocation=True,
        )

    def _build_groups(self, user_pool: cognito.UserPool) -> None:
        cognito.CfnUserPoolGroup(
            self,
            'ReadersGroup',
            user_pool_id=user_pool.user_pool_id,
            group_name=constants.READERS_GROUP,
            description=f'Members get the {constants.READ_SCOPE} scope',
        )
        cognito.CfnUserPoolGroup(
            self,
            'WritersGroup',
            user_pool_id=user_pool.user_pool_id,
            group_name=constants.WRITERS_GROUP,
            description=f'Members get the {constants.READ_SCOPE} and {constants.WRITE_SCOPE} scopes',
        )
