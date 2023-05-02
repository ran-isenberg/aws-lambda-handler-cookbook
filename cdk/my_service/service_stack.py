import os
from pathlib import Path

from aws_cdk import Aspects, Stack, Tags
from cdk_nag import AwsSolutionsChecks, NagSuppressions
from constructs import Construct
from git import Repo
from my_service.api_construct import ApiConstruct  # type: ignore

from cdk.my_service.configuration.configuration_construct import ConfigurationStore
from cdk.my_service.constants import CONFIGURATION_NAME, ENVIRONMENT, SERVICE_NAME


def get_username() -> str:
    try:
        return os.getlogin().replace('.', '-')
    except Exception:
        return 'github'


def get_stack_name() -> str:
    repo = Repo(Path.cwd())
    username = get_username()
    try:
        return f'{username}-{repo.active_branch}-{SERVICE_NAME}'
    except TypeError:
        return f'{username}-{SERVICE_NAME}'


class ServiceStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        Tags.of(self).add('service_name', 'Order')

        # This construct should be deployed in a different repo and have its own pipeline so updates can be decoupled
        # from running the service pipeline and without redeploying the service lambdas. For the sake of this template
        # example, it is deployed as part of the service stack
        self.dynamic_configuration = ConfigurationStore(self, f'{id}dynamic_conf'[0:64], ENVIRONMENT, SERVICE_NAME, CONFIGURATION_NAME)
        self.api = ApiConstruct(self, f'{id}Service'[0:64], self.dynamic_configuration.config_app.name)

        # add security check
        self._add_security_tests()

    def _add_security_tests(self) -> None:
        Aspects.of(self).add(AwsSolutionsChecks(verbose=True))
        # Suppress a specific rule for this resource
        NagSuppressions.add_stack_suppressions(
            self,
            [
                {
                    'id': 'AwsSolutions-IAM4',
                    'reason': 'policy for cloudwatch logs.'
                },
                {
                    'id': 'AwsSolutions-IAM5',
                    'reason': 'policy for cloudwatch logs.'
                },
                {
                    'id': 'AwsSolutions-APIG2',
                    'reason': 'lambda does input validation'
                },
                {
                    'id': 'AwsSolutions-APIG1',
                    'reason': 'not mandatory in a sample template'
                },
                {
                    'id': 'AwsSolutions-APIG3',
                    'reason': 'not mandatory in a sample template'
                },
                {
                    'id': 'AwsSolutions-APIG6',
                    'reason': 'not mandatory in a sample template'
                },
                {
                    'id': 'AwsSolutions-APIG4',
                    'reason': 'authorization not mandatory in a sample template'
                },
                {
                    'id': 'AwsSolutions-COG4',
                    'reason': 'not using cognito'
                },
            ],
        )
