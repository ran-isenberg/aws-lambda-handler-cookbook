import json
import os

import boto3
import requests

from cdk.service.utils import get_stack_name


def get_cdk_stack_outputs():
    """Get outputs from a specified CDK stack"""
    client = boto3.client('cloudformation')
    response = client.describe_stacks(StackName=get_stack_name())
    outputs = response['Stacks'][0]['Outputs']
    return {output['OutputKey']: output['OutputValue'] for output in outputs}


def download_swagger_json(swagger_url):
    """Download Swagger JSON from the provided URL"""
    response = requests.get(f'{swagger_url}?format=json')
    response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
    return response.json()


def save_json_to_file(json_data, file_path):
    """Save JSON data to a file"""
    with open(file_path, 'w') as file:
        json.dump(json_data, file, indent=4)


if __name__ == '__main__':
    outputs = get_cdk_stack_outputs()
    # Assuming the Swagger URL output key is 'SwaggerURL'
    swagger_url = outputs.get('SwaggerURL')
    if swagger_url:
        try:
            swagger_json = download_swagger_json(swagger_url)
            docs_path = os.path.join('docs/swagger', 'openapi.json')  # Path to save the Swagger JSON
            save_json_to_file(swagger_json, docs_path)
            print(f'Swagger JSON saved to {docs_path}')
        except requests.HTTPError as e:
            print(f'Failed to download Swagger JSON: {e}')
    else:
        print('Swagger endpoint URL not found in stack outputs.')
