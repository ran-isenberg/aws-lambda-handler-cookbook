from aws_cdk import Aws, CfnOutput, RemovalPolicy
from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from aws_cdk import aws_wafv2 as waf
from constructs import Construct


class WafToApiGatewayConstruct(Construct):
    def __init__(self, scope: Construct, id: str, api: apigateway.RestApi, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create WAF WebACL with AWS Managed Rules
        web_acl = waf.CfnWebACL(
            self,
            'ProductApiGatewayWebAcl',
            scope='REGIONAL',  # Change to CLOUDFRONT if you're using edge-optimized API
            default_action=waf.CfnWebACL.DefaultActionProperty(allow={}),
            name=f'{id}-Waf',
            visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                sampled_requests_enabled=True, cloud_watch_metrics_enabled=True, metric_name='ProductApiGatewayWebAcl'
            ),
            rules=[
                waf.CfnWebACL.RuleProperty(
                    name='Product-AWSManagedRulesCommonRuleSet',
                    priority=0,
                    override_action={'none': {}},
                    statement=waf.CfnWebACL.StatementProperty(
                        managed_rule_group_statement=waf.CfnWebACL.ManagedRuleGroupStatementProperty(
                            name='AWSManagedRulesCommonRuleSet', vendor_name='AWS'
                        )
                    ),
                    visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                        sampled_requests_enabled=True,
                        cloud_watch_metrics_enabled=True,
                        metric_name='Product-AWSManagedRulesCommonRuleSet',
                    ),
                ),
                # Block Amazon IP reputation list managed rule group
                waf.CfnWebACL.RuleProperty(
                    name='Product-AWSManagedRulesAmazonIpReputationList',
                    priority=1,
                    override_action={'none': {}},
                    statement=waf.CfnWebACL.StatementProperty(
                        managed_rule_group_statement=waf.CfnWebACL.ManagedRuleGroupStatementProperty(
                            name='AWSManagedRulesAmazonIpReputationList', vendor_name='AWS'
                        )
                    ),
                    visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                        sampled_requests_enabled=True,
                        cloud_watch_metrics_enabled=True,
                        metric_name='Product-AWSManagedRulesAmazonIpReputationList',
                    ),
                ),
                # Block Anonymous IP list managed rule group
                waf.CfnWebACL.RuleProperty(
                    name='Product-AWSManagedRulesAnonymousIpList',
                    priority=2,
                    override_action={'none': {}},
                    statement=waf.CfnWebACL.StatementProperty(
                        managed_rule_group_statement=waf.CfnWebACL.ManagedRuleGroupStatementProperty(
                            name='AWSManagedRulesAnonymousIpList', vendor_name='AWS'
                        )
                    ),
                    visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                        sampled_requests_enabled=True,
                        cloud_watch_metrics_enabled=True,
                        metric_name='Product-AWSManagedRulesAnonymousIpList',
                    ),
                ),
                # rule for blocking known Bad Inputs
                waf.CfnWebACL.RuleProperty(
                    name='Product-AWSManagedRulesKnownBadInputsRuleSet',
                    priority=3,
                    override_action={'none': {}},
                    statement=waf.CfnWebACL.StatementProperty(
                        managed_rule_group_statement=waf.CfnWebACL.ManagedRuleGroupStatementProperty(
                            name='AWSManagedRulesKnownBadInputsRuleSet', vendor_name='AWS'
                        )
                    ),
                    visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                        sampled_requests_enabled=True,
                        cloud_watch_metrics_enabled=True,
                        metric_name='Product-AWSManagedRulesKnownBadInputsRuleSet',
                    ),
                ),
            ],
        )

        # Associate WAF with API Gateway
        waf.CfnWebACLAssociation(self, 'ApiGatewayWafAssociation', resource_arn=api.deployment_stage.stage_arn, web_acl_arn=web_acl.attr_arn)

        # Enable logging for WAF, must start with 'aws-waf-logs-' prefix
        log_group_name = f'aws-waf-logs-{id}'
        # Create CloudWatch Log Group for WAF logging
        waf_log_group = logs.LogGroup(
            self,
            'WafLogGroup',
            log_group_name=log_group_name,
            retention=logs.RetentionDays.TWO_WEEKS,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Attach resource policy to allow WAF to write to the log group
        waf_log_group.add_to_resource_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                principals=[iam.AnyPrincipal()],
                actions=['logs:PutLogEvents', 'logs:CreateLogStream', 'logs:DescribeLogGroups'],
                resources=[f'{waf_log_group.log_group_arn}:*'],
            )
        )

        # Output the Log Group ARN for visibility
        CfnOutput(self, id='WafLogGroupArn', value=waf_log_group.log_group_arn).override_logical_id('WafLogGroupArn')

        # Construct the Log Group ARN manually as its not available in the CDK
        log_group_arn = f'arn:{Aws.PARTITION}:logs:{Aws.REGION}:{Aws.ACCOUNT_ID}:log-group:{log_group_name}:*'

        enable_waf_logging = waf.CfnLoggingConfiguration(
            self,
            'WafLoggingConfiguration',
            resource_arn=web_acl.attr_arn,
            log_destination_configs=[log_group_arn],
        )

        web_acl.node.add_dependency(waf_log_group)
        enable_waf_logging.node.add_dependency(web_acl)  # Ensure WebACL is created first
