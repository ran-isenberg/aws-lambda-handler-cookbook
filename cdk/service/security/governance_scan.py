from aws_cdk import (
    Aspects,
    Stack,
)
from cdk_nag import AwsSolutionsChecks, NagSuppressions


def add_security_tests(stack: Stack) -> None:
    Aspects.of(stack).add(AwsSolutionsChecks(verbose=True))

    # Suppress a specific rule for this resource
    NagSuppressions.add_stack_suppressions(
        stack,
        [
            {'id': 'AwsSolutions-IAM4', 'reason': 'policy for cloudwatch logs.'},
            {'id': 'AwsSolutions-IAM5', 'reason': 'policy for cloudwatch logs.'},
            {'id': 'AwsSolutions-APIG2', 'reason': 'lambda does input validation'},
            {'id': 'AwsSolutions-APIG1', 'reason': 'not mandatory in a sample blueprint'},
            {'id': 'AwsSolutions-APIG3', 'reason': 'not mandatory in a sample blueprint'},
            {'id': 'AwsSolutions-APIG6', 'reason': 'not mandatory in a sample blueprint'},
            {'id': 'AwsSolutions-APIG4', 'reason': 'authorization not mandatory in a sample blueprint'},
            {'id': 'AwsSolutions-COG4', 'reason': 'not using cognito'},
            {'id': 'AwsSolutions-L1', 'reason': 'False positive'},
        ],
    )
