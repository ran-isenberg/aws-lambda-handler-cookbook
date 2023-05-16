from aws_cdk import CfnOutput, Duration, RemovalPolicy, aws_apigateway
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion
from aws_cdk.aws_logs import RetentionDays
from constructs import Construct
from my_service.api_db_construct import ApiDbConstruct  # type: ignore

import cdk.my_service.constants as constants


class ApiConstruct(Construct):

    def __init__(self, scope: Construct, id_: str, appconfig_app_name: str) -> None:
        super().__init__(scope, id_)
        self.id_ = id_
        self.api_db = ApiDbConstruct(self, f'{id_}db')
        self.lambda_role = self._build_lambda_role(self.api_db.db)
        self.common_layer = self._build_common_layer()
        self.rest_api = self._build_api_gw()
        api_resource: aws_apigateway.Resource = self.rest_api.root.add_resource('api').add_resource(constants.GW_RESOURCE)
        self._add_post_lambda_integration(api_resource, self.lambda_role, self.api_db.db, appconfig_app_name)

    def _build_api_gw(self) -> aws_apigateway.RestApi:
        rest_api: aws_apigateway.RestApi = aws_apigateway.RestApi(
            self,
            'service-rest-api',
            rest_api_name='Service Rest API',
            description='This service handles /api/orders requests',
            deploy_options=aws_apigateway.StageOptions(throttling_rate_limit=2, throttling_burst_limit=10),
            cloud_watch_role=False,
        )

        CfnOutput(self, id=constants.APIGATEWAY, value=rest_api.url).override_logical_id(constants.APIGATEWAY)
        return rest_api

    def _build_lambda_role(self, db: dynamodb.Table) -> iam.Role:
        return iam.Role(
            self,
            constants.SERVICE_ROLE_ARN,
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            inline_policies={
                'dynamic_configuration':
                    iam.PolicyDocument(statements=[
                        iam.PolicyStatement(
                            actions=['appconfig:GetLatestConfiguration', 'appconfig:StartConfigurationSession'],
                            resources=['*'],
                            effect=iam.Effect.ALLOW,
                        )
                    ]),
                'dynamodb_db':
                    iam.PolicyDocument(statements=[
                        iam.PolicyStatement(actions=['dynamodb:PutItem', 'dynamodb:GetItem'], resources=[db.table_arn], effect=iam.Effect.ALLOW)
                    ]),
            },
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name=(f'service-role/{constants.LAMBDA_BASIC_EXECUTION_ROLE}'))
            ],
        )

    def _build_common_layer(self) -> PythonLayerVersion:
        return PythonLayerVersion(
            self,
            f'{self.id_}{constants.LAMBDA_LAYER_NAME}',
            entry=constants.COMMON_LAYER_BUILD_FOLDER,
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_10],
            removal_policy=RemovalPolicy.DESTROY,
        )

    def _add_post_lambda_integration(self, api_name: aws_apigateway.Resource, role: iam.Role, db: dynamodb.Table, appconfig_app_name: str):
        lambda_function = _lambda.Function(
            self,
            constants.CREATE_LAMBDA,
            runtime=_lambda.Runtime.PYTHON_3_10,
            code=_lambda.Code.from_asset(constants.BUILD_FOLDER),
            handler='service.handlers.create_order.create_order',
            environment={
                constants.POWERTOOLS_SERVICE_NAME: constants.SERVICE_NAME,  # for logger, tracer and metrics
                constants.POWER_TOOLS_LOG_LEVEL: 'DEBUG',  # for logger
                'CONFIGURATION_APP': appconfig_app_name,  # for feature flags
                'CONFIGURATION_ENV': constants.ENVIRONMENT,  # for feature flags
                'CONFIGURATION_NAME': constants.CONFIGURATION_NAME,  # for feature flags
                'CONFIGURATION_MAX_AGE_MINUTES': constants.CONFIGURATION_MAX_AGE_MINUTES,  # for feature flags
                'REST_API': 'https://www.ranthebuilder.cloud/api',  # for env vars example
                'ROLE_ARN': 'arn:partition:service:region:account-id:resource-type:resource-id',  # for env vars example
                'TABLE_NAME': db.table_name,
            },
            tracing=_lambda.Tracing.ACTIVE,
            retry_attempts=0,
            timeout=Duration.seconds(constants.API_HANDLER_LAMBDA_TIMEOUT),
            memory_size=constants.API_HANDLER_LAMBDA_MEMORY_SIZE,
            layers=[self.common_layer],
            role=role,
            log_retention=RetentionDays.ONE_DAY,
        )

        # POST /api/orders/
        api_name.add_method(http_method='POST', integration=aws_apigateway.LambdaIntegration(handler=lambda_function))
