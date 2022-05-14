from aws_cdk import Stack
from aws_lambda_handler_cookbook.service_stack.configuration.configuration_construct import ConfigurationStore
from aws_lambda_handler_cookbook.service_stack.constants import CONFIGURATION_NAME, ENVIRONMENT, SERVICE_NAME
from constructs import Construct


class CookBookConfigurationStack(Stack):

    # pylint: disable=redefined-builtin
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.dynamic_configuration = ConfigurationStore(self, 'dynamic_conf', ENVIRONMENT, SERVICE_NAME, CONFIGURATION_NAME)
