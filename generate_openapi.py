"""
This script is designed to download and save the Swagger JSON configuration from an AWS Cloud Development Kit (CDK) deployed service.
It's particularly useful for automating the process of fetching Swagger documentation for APIs created using Powertools for Lambda since their swagger endpoint support a JSON download option.
You can place the swagger file under your docs folder and publish it as part of your PR changes.
When you run the 'make pr' command, it will run automatically run this script and save its' output to the default location where it will be uploaded to GitHub pages.

Usage:
    The script accepts command-line arguments for customization:
    --out-destination: Specifies the directory where the Swagger JSON will be saved. (Default: 'docs/swagger')
    --out-filename: Specifies the filename for the saved Swagger JSON. (Default: 'openapi.json')

Example:
    python generate_openapi.py --out-destination './docs/swagger' --out-filename 'openapi.json'
"""

import argparse
import os

from aws_lambda_powertools.event_handler.openapi import OpenAPIMerge


def write_swagger(out_destination: str, out_filename: str) -> None:
    file_path = os.path.join(out_destination, out_filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    merge = OpenAPIMerge(title='AWS Lambda Handler Cookbook - Orders Service', version='1.0.0', on_conflict='warn')
    merge.discover(
        path='service/handlers',
        pattern='*/.py',
        resolver_name='app',
        recursive=True,
        project_root='.',
    )
    print(merge.get_openapi_json_schema())
    with open(file_path, 'w') as f:
        f.write(merge.get_openapi_json_schema())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download and save Swagger JSON')
    parser.add_argument(
        '--out-destination', type=str, default='docs/swagger', help='Output destination directory for Swagger JSON (default: docs/swagger)'
    )
    parser.add_argument('--out-filename', type=str, default='openapi.json', help='Output filename for Swagger JSON (default: openapi.json)')
    args = parser.parse_args()
    write_swagger(args.out_destination, args.out_filename)
