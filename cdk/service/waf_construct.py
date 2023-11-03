from aws_cdk import aws_apigateway as apigateway
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
