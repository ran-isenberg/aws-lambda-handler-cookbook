import os
from pathlib import Path

import boto3
from aws_cdk import CfnOutput, Duration, RemovalPolicy, aws_apigateway
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion
from constructs import Construct

from .constants import (
    API_HANDLER_LAMBDA_MEMORY_SIZE,
    API_HANDLER_LAMBDA_TIMEOUT,
    APIGATEWAY,
    BUILD_FOLDER,
    COMMION_LAYER_BUILD_FOLDER,
    GW_RESOURCE,
    LAMBDA_BASIC_EXECUTION_ROLE,
    METRICS_NAMESPACE,
    POWER_TOOLS_LOG_LEVEL,
    POWERTOOLS_SERVICE_NAME,
    POWERTOOLS_TRACE_DISABLED,
    SERVICE_NAME,
    SERVICE_ROLE,
    SERVICE_ROLE_ARN,
)


class LambdaConstruct(Construct):

    # pylint: disable=invalid-name, no-value-for-parameter
    def __init__(self, scope: Construct, id_: str) -> None:
        super().__init__(scope, id_)

        self.lambda_role = self._build_lambda_role()
        self.common_layer = self._build_common_layer()

        self.rest_api = self._build_api_gw()
        api_resource: aws_apigateway.Resource = self.rest_api.root.add_resource('api').add_resource(GW_RESOURCE)
        self.__add_post_lambda_integration(api_resource)

    def _build_api_gw(self) -> aws_apigateway.LambdaRestApi:
        rest_api: aws_apigateway.LambdaRestApi = aws_apigateway.RestApi(
            self,
            'cookbook-rest-api',
            rest_api_name='Lambda CookBook Rest API',
            description='This service handles /api/service requests',
            deploy_options=aws_apigateway.StageOptions(throttling_rate_limit=2, throttling_burst_limit=10),
        )

        CfnOutput(self, id=APIGATEWAY, value=rest_api.url).override_logical_id(APIGATEWAY)
        return rest_api

    def _build_lambda_role(self) -> iam.Role:
        return iam.Role(
            self,
            SERVICE_ROLE,
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name=(f'service-role/{LAMBDA_BASIC_EXECUTION_ROLE}'))],
        )

    def _build_common_layer(self) -> PythonLayerVersion:

        return PythonLayerVersion(
            self,
            'CommonLayer',
            entry=COMMION_LAYER_BUILD_FOLDER,
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_8],
            removal_policy=RemovalPolicy.DESTROY,
        )

    def __add_post_lambda_integration(self, api_name: aws_apigateway.Resource):
        lambda_function = _lambda.Function(
            self,
            'CookBookPost',
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset(BUILD_FOLDER),
            handler='service.handlers.my_handler.my_handler',
            environment={
                POWERTOOLS_SERVICE_NAME: SERVICE_NAME,  # for logger, tracer and metrics
                POWER_TOOLS_LOG_LEVEL: 'DEBUG',  # for logger
                'REST_API': 'https://www.ranthebuilder.cloud/api',  # for env vars example
                'ROLE_ARN': 'arn:partition:service:region:account-id:resource-type:resource-id',  # for env vars example
            },
            tracing=_lambda.Tracing.ACTIVE,
            retry_attempts=0,
            timeout=Duration.seconds(API_HANDLER_LAMBDA_TIMEOUT),
            memory_size=API_HANDLER_LAMBDA_MEMORY_SIZE,
            layers=[self.common_layer],
        )

        # POST /api/service/
        api_name.add_method(http_method='POST', integration=aws_apigateway.LambdaIntegration(handler=lambda_function))
