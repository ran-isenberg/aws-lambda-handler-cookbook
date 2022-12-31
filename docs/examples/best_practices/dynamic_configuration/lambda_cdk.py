from aws_cdk import Duration, aws_apigateway
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda

import cdk.my_service.constants as constants


def _build_lambda_role(self) -> iam.Role:
    return iam.Role(
        self,
        constants.SERVICE_ROLE,
        assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
        inline_policies={
            'dynamic_configuration':
                iam.PolicyDocument(statements=[
                    iam.PolicyStatement(actions=['appconfig:GetLatestConfiguration', 'appconfig:StartConfigurationSession'], resources=['*'],
                                        effect=iam.Effect.ALLOW),
                ]),
        },
        managed_policies=[
            iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name=(f'service-role/{constants.LAMBDA_BASIC_EXECUTION_ROLE}'))
        ],
    )


def _build_lambda_function(self, api_name: aws_apigateway.Resource, role: iam.Role) -> _lambda.Function:
    return _lambda.Function(
        self,
        'ServicePost',
        runtime=_lambda.Runtime.PYTHON_3_8,
        code=_lambda.Code.from_asset(constants.BUILD_FOLDER),
        handler='service.handlers.create_order.create_order',
        environment={
            constants.POWERTOOLS_SERVICE_NAME: constants.SERVICE_NAME,  # for logger, tracer and metrics
            constants.POWER_TOOLS_LOG_LEVEL: 'DEBUG',  # for logger
            'REST_API': 'https://www.ranthebuilder.cloud/api',  # for env vars example
            'ROLE_ARN': 'arn:partition:service:region:account-id:resource-type:resource-id',  # for env vars example
            'CONFIGURATION_APP': constants.SERVICE_NAME,
            'CONFIGURATION_ENV': constants.ENVIRONMENT,
            'CONFIGURATION_NAME': constants.CONFIGURATION_NAME,
            'CONFIGURATION_MAX_AGE_MINUTES': constants.CONFIGURATION_MAX_AGE_MINUTES,
        },
        tracing=_lambda.Tracing.ACTIVE,
        retry_attempts=0,
        timeout=Duration.seconds(constants.API_HANDLER_LAMBDA_TIMEOUT),
        memory_size=constants.API_HANDLER_LAMBDA_MEMORY_SIZE,
        role=role,
    )
