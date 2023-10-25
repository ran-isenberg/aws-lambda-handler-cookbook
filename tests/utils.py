import json
import random
import string
from typing import Any, Optional

import boto3
from aws_lambda_powertools.utilities.typing import LambdaContext

from cdk.service.utils import get_stack_name


def generate_random_string(length: int = 3):
    letters = string.ascii_letters
    random_string = ''.join(random.choice(letters) for _ in range(length))
    return random_string


def generate_context() -> LambdaContext:
    context = LambdaContext()
    context._aws_request_id = '888888'
    context._function_name = 'test'
    context._memory_limit_in_mb = 128
    context._invoked_function_arn = 'arn:aws:lambda:eu-west-1:123456789012:function:test'
    return context


# example taken from AWS Lambda Powertools test files
# https://github.com/awslabs/aws-lambda-powertools-python/blob/develop/tests/events/apiGatewayProxyEvent.json
def generate_api_gw_event(body: Optional[dict[str, Any]]) -> dict[str, Any]:
    return {
        'version': '1.0',
        'resource': '/api/orders',
        'path': '/api/orders',
        'httpMethod': 'POST',
        'headers': {'Header1': 'value1', 'Header2': 'value2'},
        'multiValueHeaders': {'Header1': ['value1'], 'Header2': ['value1', 'value2']},
        'queryStringParameters': {'parameter1': 'value1', 'parameter2': 'value'},
        'multiValueQueryStringParameters': {'parameter1': ['value1', 'value2'], 'parameter2': ['value']},
        'requestContext': {
            'accountId': '123456789012',
            'apiId': 'id',
            'authorizer': {'claims': None, 'scopes': None},
            'domainName': 'id.execute-api.us-east-1.amazonaws.com',
            'domainPrefix': 'id',
            'extendedRequestId': 'request-id',
            'httpMethod': 'POST',
            'identity': {
                'accessKey': None,
                'accountId': None,
                'caller': None,
                'cognitoAuthenticationProvider': None,
                'cognitoAuthenticationType': None,
                'cognitoIdentityId': None,
                'cognitoIdentityPoolId': None,
                'principalOrgId': None,
                'sourceIp': '192.168.0.1/32',
                'user': None,
                'userAgent': 'user-agent',
                'userArn': None,
                'clientCert': {
                    'clientCertPem': 'CERT_CONTENT',
                    'subjectDN': 'www.example.com',
                    'issuerDN': 'Example issuer',
                    'serialNumber': 'a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1',
                    'validity': {'notBefore': 'May 28 12:30:02 2019 GMT', 'notAfter': 'Aug  5 09:36:04 2021 GMT'},
                },
            },
            'path': '/api/orders',
            'protocol': 'HTTP/1.1',
            'requestId': 'id=',
            'requestTime': '04/Mar/2020:19:15:17 +0000',
            'requestTimeEpoch': 1583349317135,
            'resourceId': None,
            'resourcePath': '/api/orders',
            'stage': '$default',
        },
        'pathParameters': None,
        'stageVariables': None,
        'body': 'Hello from Lambda!' if body is None else json.dumps(body),
        'isBase64Encoded': True,
    }


def get_stack_output(output_key: str) -> str:
    client = boto3.client('cloudformation')
    response = client.describe_stacks(StackName=get_stack_name())
    stack_outputs = response['Stacks'][0]['Outputs']
    for value in stack_outputs:
        if str(value['OutputKey']) == output_key:
            return value['OutputValue']
    raise Exception(f'stack output {output_key} was not found')
