from aws_cdk import Stack
from constructs import Construct

from cdk.my_service.service_stack.configuration.configuration_construct import ConfigurationStore
from cdk.my_service.service_stack.constants import CONFIGURATION_NAME, ENVIRONMENT, SERVICE_NAME
from cdk.my_service.service_stack.service_construct import ApiConstruct


class ServiceStack(Stack):

    # pylint: disable=redefined-builtin
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # This construct should be deployed in a different repo and have its own pipeline so updates can be decoupled from running
        # the service pipeline and without redeploying the service lambdas. For the sake of this template example,
        # it is deployed as part of the service stack
        self.dynamic_configuration = ConfigurationStore(self, 'dynamic_conf', ENVIRONMENT, SERVICE_NAME, CONFIGURATION_NAME)

        self.lambdas = ApiConstruct(self, 'Service')
