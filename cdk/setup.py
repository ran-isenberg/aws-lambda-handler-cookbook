#!/usr/bin/env python
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

setup(
    name='service-cdk',
    version='3.1',
    description='CDK code for deploying an AWS Lambda handler that implements the best practices described at https://www.ranthebuilder.cloud',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3.10',
    ],
    url='https://github.com/ran-isenberg/aws-lambda-handler-cookbook',
    author='Ran Isenberg',
    author_email='ran.isenberg@ranthebuilder.cloud',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    package_data={'': ['*.json']},
    include_package_data=True,
    python_requires='>=3.10',
    install_requires=[],
)
