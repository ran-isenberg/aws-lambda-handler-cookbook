#!/usr/bin/env python
from os import getenv, path

from setuptools import find_packages, setup

# pylint: disable=invalid-name
here = path.abspath(path.dirname(__file__))

setup(
    name='aws-lambda-handler-cookbook',
    version='1.0',
    description='CDK code for deploying an AWS Lambda handler that implements the best practices described at https://www.ranthebuilder.cloud',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3.8',
    ],
    url='https://github.com/ran-isenberg/aws-lambda-handler-cookbook',
    author='Ran Isenberg',
    author_email='ran.isenberg@ranthebuilder.cloud',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    package_data={'': ['*.json']},
    include_package_data=True,
    python_requires='>=3.8',
    install_requires=[
        'aws-cdk-lib>=2.0.0',
        'constructs>=10.0.0',
        'aws-cdk.aws-lambda-python-alpha==2.27.0-alpha.0',
    ],
)
