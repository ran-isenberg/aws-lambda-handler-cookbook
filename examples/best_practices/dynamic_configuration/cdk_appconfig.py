from aws_cdk import Stack
from constructs import Construct

from cdk.service.configuration.configuration_construct import ConfigurationStore
from cdk.service.constants import CONFIGURATION_NAME, ENVIRONMENT, SERVICE_NAME


class DynamicConfigurationStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.dynamic_configuration = ConfigurationStore(self, 'dynamic_conf', ENVIRONMENT, SERVICE_NAME, CONFIGURATION_NAME)
