from aws_cdk import core
from aws_lambda_handler_cookbook.service_stack.cookbook_construct import LambdaConstruct


class CookBookStack(core.Stack):

    # pylint: disable=redefined-builtin
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        self.lambdas = LambdaConstruct(self, 'Service')
