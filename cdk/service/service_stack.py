from aws_cdk import Stack, Tags, Validations
from cdk_nag import AwsSolutionsChecks
from constructs import Construct

from cdk.service.api_construct import ApiConstruct
from cdk.service.auth_construct import AuthConstruct
from cdk.service.configuration.configuration_construct import ConfigurationStore
from cdk.service.constants import CONFIGURATION_NAME, ENVIRONMENT, OWNER_TAG, SERVICE_NAME, SERVICE_NAME_TAG
from cdk.service.utils import get_construct_name, get_username


class ServiceStack(Stack):
    def __init__(self, scope: Construct, id: str, is_production_env: bool, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        self._add_stack_tags()

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
        self.auth = AuthConstruct(self, get_construct_name(stack_prefix=id, construct_name='Auth'))
        self.api = ApiConstruct(
            self,
            get_construct_name(stack_prefix=id, construct_name='Crud'),
            self.dynamic_configuration.app_name,
            is_production_env=is_production_env,
            user_pool_id=self.auth.user_pool.user_pool_id,
            user_pool_client_id=self.auth.user_pool_client.user_pool_client_id,
            user_pool_jwks=self.auth.jwks,
        )

        # add security check
        self._add_security_tests()

    def _add_stack_tags(self) -> None:
        # best practice to help identify resources in the console
        Tags.of(self).add(SERVICE_NAME_TAG, SERVICE_NAME)
        Tags.of(self).add(OWNER_TAG, get_username())

    def _add_security_tests(self) -> None:
        Validations.of(self).add_plugins(AwsSolutionsChecks(self, verbose=True))
        # Acknowledge (suppress) specific cdk-nag findings for the whole stack.
        self._acknowledge_nag_findings(
            {
                'AwsSolutions-IAM4[Policy::arn:<AWS::Partition>:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole]': 'policy for cloudwatch logs.',
                'AwsSolutions-IAM4[Policy::arn:<AWS::Partition>:iam::aws:policy/AWSLambdaManagedEC2ResourceOperator]': 'managed policy required for the Lambda managed EC2 capacity provider.',
                'AwsSolutions-IAM5[Resource::*]': 'policy for cloudwatch logs.',
                'AwsSolutions-APIG2': 'lambda does input validation',
                'AwsSolutions-APIG1': 'not mandatory in a sample blueprint',
                'AwsSolutions-APIG3': 'not mandatory in a sample blueprint',
                'AwsSolutions-APIG6': 'not mandatory in a sample blueprint',
                'AwsSolutions-APIG4': 'authorization is enforced inside the Lambda functions by the Powertools JWTVerifier (Cognito access tokens and scopes)',
                'AwsSolutions-COG2': 'MFA is not required: the pool is admin-provisioned, has no self sign up and is a sample blueprint',
                'AwsSolutions-COG3': 'advanced security mode is a paid add-on and is not mandatory in a sample blueprint',
                'AwsSolutions-COG8': 'the Essentials feature plan is enough (it supports the pre token generation V2 trigger); the Plus plan is a paid tier not needed in a sample blueprint',
                'AwsSolutions-COG4': 'no API Gateway Cognito authorizer: tokens are verified in the Lambda functions by the Powertools JWTVerifier',
                'AwsSolutions-L1': 'False positive',
            }
        )

    def _acknowledge_nag_findings(self, findings: dict[str, str]) -> None:
        # cdk-nag v3 delegates suppression to CDK's native Validations.acknowledge(), but that API
        # rejects any rule id containing more than one '::' delimiter. Granular IAM findings carry
        # such ids (e.g. 'AwsSolutions-IAM4[Policy::arn:<AWS::Partition>:iam::aws:policy/...]'), so we
        # record the acknowledgment metadata directly under the key cdk-nag reads. This matches its
        # internal isAcknowledged() lookup exactly and works for both simple and granular finding ids.
        for finding_id, reason in findings.items():
            self.node.add_metadata(Validations.ACKNOWLEDGED_RULES_METADATA_KEY, {finding_id: reason})
