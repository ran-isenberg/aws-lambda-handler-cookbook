#!/usr/bin/env python
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

setup(
    name='cdk',
    version='1.0',
    description='CDK code for deploying an AWS Lambda handler that implements the best practices described at https://www.ranthebuilder.cloud',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3.9',
    ],
    url='https://github.com/ran-isenberg/aws-lambda-handler-cookbook',
    author='Ran Isenberg',
    author_email='ran.isenberg@ranthebuilder.cloud',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    package_data={'': ['*.json']},
    include_package_data=True,
    python_requires='>=3.9',
    install_requires=[
        'aws-cdk-lib>=2.0.0',
        'constructs>=10.0.0',
        'cdk-nag>2.0.0',
        'aws-cdk.aws-lambda-python-alpha==2.44.0-alpha.0',
    ],
)
