from typing import Sequence

from aws_cdk import CfnOutput, CfnResource, RemovalPolicy, Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_logs as logs
from aws_cdk.aws_ec2_alpha import IpAddresses, IpCidr, SubnetV2, VpcV2
from cdk_nag import NagSuppressions
from constructs import Construct

import cdk.service.constants as constants


class LambdaManagedInstanceConstruct(Construct):
    def __init__(self, scope: Construct, id_: str, architecture: _lambda.Architecture, availability_zones: list[str]) -> None:
        super().__init__(scope, id_)
        self.id_ = id_
        self.architecture = architecture  # capacity provider architecture must match the attached function
        self.vpc, self.subnets, self.security_group = self._build_networking(availability_zones)
        self.operator_role = self._build_operator_role()
        self.capacity_provider = self._build_capacity_provider(
            subnet_ids=[s.subnet_id for s in self.subnets],
            security_group_id=self.security_group.security_group_id,
            operator_role_arn=self.operator_role.role_arn,
        )
        self.capacity_provider_arn = self.capacity_provider.get_att('Arn').to_string()

        CfnOutput(self, 'ManagedInstanceCapacityProviderName', value=self._capacity_provider_name())

    def _build_networking(self, availability_zones: list[str]) -> tuple[VpcV2, Sequence[ec2.ISubnet], ec2.SecurityGroup]:
        vpc = VpcV2(
            self,
            constants.MANAGED_INSTANCE_VPC,
            primary_address_block=IpAddresses.ipv4(
                constants.MANAGED_INSTANCE_VPC_CIDR,
                cidr_block_name=f'{constants.MANAGED_INSTANCE_VPC}Primary',
            ),
            enable_dns_hostnames=True,
            enable_dns_support=True,
        )
        self._add_flow_log(vpc)
        subnets = [
            SubnetV2(
                self,
                f'{constants.MANAGED_INSTANCE_VPC}Subnet{i}',
                vpc=vpc,
                availability_zone=az,
                ipv4_cidr_block=IpCidr(f'10.0.{i + 1}.0/24'),
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
            )
            for i, az in enumerate(availability_zones)
        ]
        security_group = ec2.SecurityGroup(
            self,
            constants.MANAGED_INSTANCE_SECURITY_GROUP,
            vpc=vpc,
            description='Security group for Lambda Managed Instances capacity provider',
            allow_all_outbound=True,
        )
        self._add_dynamodb_gateway_endpoint(vpc, subnets)
        self._add_interface_endpoints(vpc, subnets, security_group)
        return vpc, subnets, security_group

    def _add_dynamodb_gateway_endpoint(self, vpc: VpcV2, subnets: Sequence[ec2.ISubnet]) -> ec2.GatewayVpcEndpoint:
        return ec2.GatewayVpcEndpoint(
            self,
            f'{constants.MANAGED_INSTANCE_VPC}DynamoDbEndpoint',
            vpc=vpc,
            service=ec2.GatewayVpcEndpointAwsService.DYNAMODB,
            subnets=[ec2.SubnetSelection(subnets=subnets)],
        )

    def _add_interface_endpoints(self, vpc: VpcV2, subnets: Sequence[ec2.ISubnet], client_sg: ec2.SecurityGroup) -> None:
        endpoints_sg = ec2.SecurityGroup(
            self,
            f'{constants.MANAGED_INSTANCE_VPC}EndpointsSg',
            vpc=vpc,
            description='Allows HTTPS from the capacity provider to VPC interface endpoints',
            allow_all_outbound=False,
        )
        endpoints_sg.add_ingress_rule(peer=client_sg, connection=ec2.Port.tcp(443), description='HTTPS from capacity provider instances')
        NagSuppressions.add_resource_suppressions(
            endpoints_sg,
            [
                {
                    'id': 'CdkNagValidationFailure',
                    'reason': (
                        'Ingress CIDR is a CFN intrinsic (VPC CidrBlock) added by InterfaceVpcEndpoint; '
                        'it resolves to the private VPC CIDR, not 0.0.0.0/0.'
                    ),
                },
            ],
        )

        for endpoint_id, service in (
            ('CloudWatchLogsEndpoint', ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS),
            ('XRayEndpoint', ec2.InterfaceVpcEndpointAwsService.XRAY),
        ):
            ec2.InterfaceVpcEndpoint(
                self,
                f'{constants.MANAGED_INSTANCE_VPC}{endpoint_id}',
                vpc=vpc,
                service=service,
                subnets=ec2.SubnetSelection(subnets=subnets),
                security_groups=[endpoints_sg],
                private_dns_enabled=True,
            )

    def _add_flow_log(self, vpc: VpcV2) -> ec2.FlowLog:
        log_group = logs.LogGroup(
            self,
            f'{constants.MANAGED_INSTANCE_VPC}FlowLogGroup',
            retention=logs.RetentionDays.THREE_DAYS,
            removal_policy=RemovalPolicy.DESTROY,
        )
        return ec2.FlowLog(
            self,
            f'{constants.MANAGED_INSTANCE_VPC}FlowLog',
            resource_type=ec2.FlowLogResourceType.from_vpc(vpc),
            destination=ec2.FlowLogDestination.to_cloud_watch_logs(log_group),
            traffic_type=ec2.FlowLogTrafficType.REJECT,
        )

    def _build_operator_role(self) -> iam.Role:
        return iam.Role(
            self,
            constants.MANAGED_INSTANCE_OPERATOR_ROLE,
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            description='Allows Lambda to launch and manage EC2 instances for the capacity provider',
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(constants.MANAGED_INSTANCE_OPERATOR_POLICY),
            ],
        )

    def _capacity_provider_name(self) -> str:
        return f'{Stack.of(self).stack_name}-{constants.MANAGED_INSTANCE_CAPACITY_PROVIDER}'

    def _build_capacity_provider(self, subnet_ids: list[str], security_group_id: str, operator_role_arn: str) -> CfnResource:
        name = self._capacity_provider_name()
        return CfnResource(
            self,
            name,
            type='AWS::Lambda::CapacityProvider',
            properties={
                'CapacityProviderName': name,
                'VpcConfig': {
                    'SubnetIds': subnet_ids,
                    'SecurityGroupIds': [security_group_id],
                },
                'PermissionsConfig': {
                    'CapacityProviderOperatorRoleArn': operator_role_arn,
                },
                'InstanceRequirements': {
                    'Architectures': [self.architecture.name],
                },
                'CapacityProviderScalingConfig': {
                    'MaxVCpuCount': constants.MANAGED_INSTANCE_MAX_VCPU,
                },
            },
        )
