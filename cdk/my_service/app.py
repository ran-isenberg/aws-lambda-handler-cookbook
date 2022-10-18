#!/usr/bin/env python3
import os

from aws_cdk import App, Environment
from boto3 import client, session

from cdk.my_service.service_stack.constants import get_stack_name
from cdk.my_service.service_stack.service_stack import ServiceStack

account = client('sts').get_caller_identity()['Account']
region = session.Session().region_name
app = App()
my_stack = ServiceStack(app, get_stack_name(),
                        env=Environment(account=os.environ.get('AWS_DEFAULT_ACCOUNT', account), region=os.environ.get('AWS_DEFAULT_REGION', region)))

app.synth()
