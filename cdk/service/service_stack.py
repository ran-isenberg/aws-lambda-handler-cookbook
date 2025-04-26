from aws_cdk import (
    Stack,
    Tags,
)
from constructs import Construct

from cdk.service.api_construct import ApiConstruct
from cdk.service.configuration.configuration_construct import ConfigurationStore
from cdk.service.constants import CONFIGURATION_NAME, ENVIRONMENT, OWNER_TAG, SERVICE_NAME, SERVICE_NAME_TAG
from cdk.service.security.governance_scan import add_security_tests
from cdk.service.utils import get_construct_name, get_username


class ServiceStack(Stack):
    def __init__(self, scope: Construct, id: str, is_production_env: bool, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        self._add_stack_tags(self.code_sign.config)

        # This construct should be deployed in a different repo and have its own pipeline so updates can be decoupled
        # from running the service pipeline and without redeploying the service lambdas. For the sake of this blueprint
        # example, it is deployed as part of the service stack
        self.dynamic_configuration = ConfigurationStore(
            self,
            get_construct_name(stack_prefix=id, construct_name='DynamicConf'),
            ENVIRONMENT,
            SERVICE_NAME,
            CONFIGURATION_NAME,
        )

        self.api = ApiConstruct(
            self,
            get_construct_name(stack_prefix=id, construct_name='Crud'),
            self.dynamic_configuration.app_name,
            is_production_env=is_production_env,
        )

        # add security check
        add_security_tests(stack=self)

    def _add_stack_tags(self) -> None:
        # best practice to help identify resources in the console
        Tags.of(self).add(SERVICE_NAME_TAG, SERVICE_NAME)
        Tags.of(self).add(OWNER_TAG, get_username())
