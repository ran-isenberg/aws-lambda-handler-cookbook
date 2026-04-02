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
import importlib
import json
import os
import shutil
import sys
from pathlib import Path

import aws_lambda_powertools.event_handler.openapi as _openapi_pkg

# Patch the installed merge.py with our version that supports the shared-resolver pattern
# (project_root param and dependent file discovery). The current Powertools release (3.24+)
# removed this support. This works in both local venvs and CI (GitHub Actions) since
# we resolve the target path dynamically from the installed package location.
# workaround until https://github.com/aws-powertools/powertools-lambda-python/pull/7939 merged
_MERGE_SRC = Path(__file__).parent / 'merge.py'
_MERGE_DST = Path(_openapi_pkg.__file__).parent / 'merge.py'
shutil.copy2(_MERGE_SRC, _MERGE_DST)

# Force Python to reload the patched module
sys.modules.pop('aws_lambda_powertools.event_handler.openapi.merge', None)
importlib.reload(_openapi_pkg)

from aws_lambda_powertools.event_handler.openapi import OpenAPIMerge  # noqa: E402

# Dummy environment variables required for handler module loading.
# When merge.py imports handler files to discover routes, decorators like
# @init_environment_variables validate env vars at import time.
# These dummy values allow the module to load without a real Lambda environment.
_DUMMY_ENV_VARS = {
    'POWERTOOLS_SERVICE_NAME': 'orders',
    'POWERTOOLS_TRACE_DISABLED': 'true',
    'LOG_LEVEL': 'INFO',
    'IDEMPOTENCY_TABLE_NAME': 'dummy',
    'CONFIGURATION_APP': 'dummy',
    'CONFIGURATION_ENV': 'dummy',
    'CONFIGURATION_NAME': 'dummy',
    'CONFIGURATION_MAX_AGE_MINUTES': '1',
    'REST_API': 'https://dummy.execute-api.us-east-1.amazonaws.com',
    'ROLE_ARN': 'arn:aws:iam::123456789012:role/dummy',
    'TABLE_NAME': 'dummy',
}


def _print_discovery_info(merge: OpenAPIMerge, files: list, schema_json: str) -> None:
    print(f'Discovered {len(files)} resolver file(s):')
    for f in files:
        print(f'  - Resolver: {f}')
    for resolver_file, deps in merge.dependent_files.items():
        print(f'  Resolver {resolver_file.name} has {len(deps)} dependent handler(s):')
        for dep in deps:
            print(f'    - Handler: {dep}')
    paths = json.loads(schema_json).get('paths', {})
    print(f'Generated {len(paths)} API path(s):')
    for path, methods in paths.items():
        for method in methods:
            print(f'  - {method.upper()} {path}')


def write_swagger(out_destination: str, out_filename: str) -> None:
    # Set dummy env vars only for keys not already present
    for key, value in _DUMMY_ENV_VARS.items():
        os.environ.setdefault(key, value)

    file_path = os.path.join(out_destination, out_filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    merge = OpenAPIMerge(title='AWS Lambda Handler Cookbook - Orders Service', version='1.0.0', on_conflict='warn')
    files = merge.discover(
        path='service/handlers',
        pattern='**/*.py',
        resolver_name='app',
        recursive=True,
        project_root='.',
    )
    schema_json = merge.get_openapi_json_schema()
    _print_discovery_info(merge, files, schema_json)

    with open(file_path, 'w') as f:
        f.write(schema_json)
    print(f'OpenAPI schema written to {file_path}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download and save Swagger JSON')
    parser.add_argument(
        '--out-destination', type=str, default='docs/swagger', help='Output destination directory for Swagger JSON (default: docs/swagger)'
    )
    parser.add_argument('--out-filename', type=str, default='openapi.json', help='Output filename for Swagger JSON (default: openapi.json)')
    args = parser.parse_args()
    write_swagger(args.out_destination, args.out_filename)
