import aws_cdk.aws_logs as logs
from aws_cdk import (
    aws_appsync as appsync,
)
from aws_cdk import (
    aws_iam as iam,
)
from aws_cdk import (
    aws_wafv2 as wafv2,
)
from aws_cdk.aws_lambda import Function
from constructs import Construct


class AppSyncEventsApi(Construct):
    def __init__(self, scope: Construct, id_: str, web_acl_arn: str, lambda_data_source: Function) -> None:
        super().__init__(scope, id_)
        self.id_ = id_
        api_key_provider = appsync.AppSyncAuthProvider(authorization_type=appsync.AppSyncAuthorizationType.API_KEY)

        self.api = appsync.EventApi(
            self,
            'api',
            api_name='my-events-api',
            owner_contact='ran.isenberg at ranthebuilder.cloud',
            authorization_config=appsync.EventApiAuthConfig(
                auth_providers=[api_key_provider],
                connection_auth_mode_types=[appsync.AppSyncAuthorizationType.API_KEY],
                default_publish_auth_mode_types=[appsync.AppSyncAuthorizationType.API_KEY],
                default_subscribe_auth_mode_types=[appsync.AppSyncAuthorizationType.API_KEY],
            ),
            log_config=appsync.AppSyncLogConfig(field_log_level=appsync.AppSyncFieldLogLevel.INFO, retention=logs.RetentionDays.ONE_WEEK),
        )

        self.api.add_channel_namespace('default')

        # Associate the WAF WebACL to the AppSync API
        wafv2.CfnWebACLAssociation(
            self,
            'EventsApiWafAssociation',
            resource_arn=self.api.api_arn,
            web_acl_arn=web_acl_arn,
        )

        # Create IAM Role for AppSync to invoke the Lambda
        self.lambda_role = iam.Role(
            self,
            'AppSyncInvokeLambdaRole',
            assumed_by=iam.ServicePrincipal('appsync.amazonaws.com'),
            description='Role for AppSync to invoke the Lambda',
        )

        # Grant invoke permission to AppSync role
        lambda_data_source.grant_invoke(self.lambda_role)

        # Create Lambda DataSource manually
        self.lambda_data_source = appsync.CfnDataSource(
            self,
            'MyLambdaDataSource',
            api_id=self.api.api_id,
            name='myLambdaDataSource',
            type='AWS_LAMBDA',
            lambda_config=appsync.CfnDataSource.LambdaConfigProperty(lambda_function_arn=lambda_data_source.function_arn),
            service_role_arn=self.lambda_role.role_arn,
            description='Mono Lambda to control publish and subscribe',
        )
