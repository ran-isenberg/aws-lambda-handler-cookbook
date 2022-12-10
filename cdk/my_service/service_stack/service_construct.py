import my_service.service_stack.constants as constants
from aws_cdk import CfnOutput, Duration, RemovalPolicy, aws_apigateway
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_logs
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion
from constructs import Construct


class ApiConstruct(Construct):

    def __init__(self, scope: Construct, id_: str, appconfig_app_name: str) -> None:
        super().__init__(scope, id_)

        self.db = self._build_db(id_)
        self.lambda_role = self._build_lambda_role(self.db)
        self.common_layer = self._build_common_layer()
        self.rest_api = self._build_api_gw()
        api_resource: aws_apigateway.Resource = self.rest_api.root.add_resource('api').add_resource(constants.GW_RESOURCE)
        self.__add_post_lambda_integration(api_resource, self.lambda_role, self.db, appconfig_app_name)

    def _build_db(self, id_prefix: str) -> dynamodb.Table:
        table_id = f'{id_prefix}{constants.TABLE_NAME}'
        table = dynamodb.Table(
            self,
            table_id,
            table_name=table_id,
            partition_key=dynamodb.Attribute(name='order_id', type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            point_in_time_recovery=True,
            removal_policy=RemovalPolicy.DESTROY,
        )
        CfnOutput(self, id=constants.TABLE_NAME_OUTPUT, value=table.table_name).override_logical_id(constants.TABLE_NAME_OUTPUT)
        return table

    def _build_api_gw(self) -> aws_apigateway.LambdaRestApi:
        rest_api: aws_apigateway.LambdaRestApi = aws_apigateway.RestApi(
            self,
            'service-rest-api',
            rest_api_name='Service Rest API',
            description='This service handles /api/orders requests',
            deploy_options=aws_apigateway.StageOptions(throttling_rate_limit=2, throttling_burst_limit=10),
        )

        CfnOutput(self, id=constants.APIGATEWAY, value=rest_api.url).override_logical_id(constants.APIGATEWAY)
        return rest_api

    def _build_lambda_role(self, db: dynamodb.Table) -> iam.Role:
        return iam.Role(
            self,
            constants.SERVICE_ROLE,
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
                    iam.PolicyDocument(
                        statements=[iam.PolicyStatement(actions=['dynamodb:PutItem'], resources=[db.table_arn], effect=iam.Effect.ALLOW)]),
            },
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name=(f'service-role/{constants.LAMBDA_BASIC_EXECUTION_ROLE}'))
            ],
        )

    def _build_common_layer(self) -> PythonLayerVersion:
        return PythonLayerVersion(
            self,
            'CommonLayer',
            entry=constants.COMMON_LAYER_BUILD_FOLDER,
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            removal_policy=RemovalPolicy.DESTROY,
        )

    def __add_post_lambda_integration(self, api_name: aws_apigateway.Resource, role: iam.Role, db: dynamodb.Table, appconfig_app_name: str):
        lambda_function = _lambda.Function(
            self,
            'ServicePost',
            runtime=_lambda.Runtime.PYTHON_3_9,
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
            log_retention=aws_logs.RetentionDays.ONE_DAY,
        )

        # POST /api/orders/
        api_name.add_method(http_method='POST', integration=aws_apigateway.LambdaIntegration(handler=lambda_function))
