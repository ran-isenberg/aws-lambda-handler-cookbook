from aws_cdk import App
from aws_cdk.assertions import Template

from cdk.service.service_stack import ServiceStack


def test_synthesizes_properly():
    app = App()

    service_stack = ServiceStack(app, 'service-test', is_production_env=True)

    # Prepare the stack for assertions.
    template = Template.from_stack(service_stack)

    # verify that we have one API GW, that is it not deleted by mistake
    template.resource_count_is('AWS::ApiGateway::RestApi', 1)
    template.resource_count_is('AWS::DynamoDB::Table', 2)  # main db and one for idempotency
