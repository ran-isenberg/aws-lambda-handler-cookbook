from aws_cdk import Duration
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda

import cdk.service.constants as constants


def _build_lambda_role(self, db: dynamodb.Table) -> iam.Role:
    return iam.Role(
        self,
        constants.SERVICE_ROLE,
        assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
        inline_policies={
            'dynamic_configuration': iam.PolicyDocument(
                statements=[
                    iam.PolicyStatement(
                        actions=['appconfig:GetLatestConfiguration', 'appconfig:StartConfigurationSession'],
                        resources=['*'],
                        effect=iam.Effect.ALLOW,
                    )
                ]
            ),
            'dynamodb_db': iam.PolicyDocument(
                statements=[iam.PolicyStatement(actions=['dynamodb:PutItem', 'dynamodb:GetItem'], resources=[db.table_arn], effect=iam.Effect.ALLOW)]
            ),
        },
        managed_policies=[
            iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name=(f'service-role/{constants.LAMBDA_BASIC_EXECUTION_ROLE}'))
        ],
    )


def _build_lambda_function(self, role: iam.Role, db: dynamodb.Table, appconfig_app_name: str) -> _lambda.Function:
    return _lambda.Function(
        self,
        'ServicePost',
        runtime=_lambda.Runtime.PYTHON_3_11,
        code=_lambda.Code.from_asset(constants.BUILD_FOLDER),
        handler='service.handlers.create_order.create_order',
        environment={
            constants.POWERTOOLS_SERVICE_NAME: constants.SERVICE_NAME,  # for logger, tracer and metrics
            constants.POWER_TOOLS_LOG_LEVEL: 'DEBUG',  # for logger
            'REST_API': 'https://www.ranthebuilder.cloud/api',  # for env vars example
            'ROLE_ARN': 'arn:partition:service:region:account-id:resource-type:resource-id',  # for env vars example
            'CONFIGURATION_APP': appconfig_app_name,  # for feature flags
            'CONFIGURATION_ENV': constants.ENVIRONMENT,
            'CONFIGURATION_NAME': constants.CONFIGURATION_NAME,
            'CONFIGURATION_MAX_AGE_MINUTES': constants.CONFIGURATION_MAX_AGE_MINUTES,
            'TABLE_NAME': db.table_name,
        },
        tracing=_lambda.Tracing.ACTIVE,
        retry_attempts=0,
        timeout=Duration.seconds(constants.API_HANDLER_LAMBDA_TIMEOUT),
        memory_size=constants.API_HANDLER_LAMBDA_MEMORY_SIZE,
        role=role,
    )
