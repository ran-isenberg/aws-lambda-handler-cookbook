from aws_cdk import Stack
from aws_lambda_handler_cookbook.service_stack.cookbook_construct import LambdaConstruct
from constructs import Construct


class CookBookStack(Stack):

    # pylint: disable=redefined-builtin
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        self.lambdas = LambdaConstruct(self, 'Service')
