from aws_cdk import Stack
from aws_lambda_handler_cookbook.service_stack.configuration.configuration_construct import ConfigurationStore
from aws_lambda_handler_cookbook.service_stack.constants import CONFIGURATION_NAME, ENVIRONMENT, SERVICE_NAME
from aws_lambda_handler_cookbook.service_stack.cookbook_construct import LambdaConstruct
from constructs import Construct


class CookBookStack(Stack):

    # pylint: disable=redefined-builtin
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # This construct should be deployed in a different repo and have its own pipeline so updates can be decoupled from running the service pipeline and without
        # redeploying the service lambdas. For the sake of this template example, it is deployed as part of the service stack
        self.dynamic_configuration = ConfigurationStore(self, 'dynamic_conf', ENVIRONMENT, SERVICE_NAME, CONFIGURATION_NAME)

        self.lambdas = LambdaConstruct(self, 'Service')
