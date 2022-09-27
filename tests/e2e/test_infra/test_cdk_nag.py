from aws_cdk import App, Aspects
from cdk_nag import AwsSolutionsChecks, HIPAASecurityChecks

from cdk.my_service.service_stack.service_stack import ServiceStack


def test_cdk_nag_default():
    app = App()

    service_stack = ServiceStack(app, 'service-test')
    Aspects.of(service_stack).add(AwsSolutionsChecks(verbose=True))


def test_cdk_nag_hipaa():
    app = App()

    service_stack = ServiceStack(app, 'service-test')
    Aspects.of(service_stack).add(HIPAASecurityChecks(verbose=True))
