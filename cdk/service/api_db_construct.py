from aws_cdk import CfnOutput, RemovalPolicy
from aws_cdk import aws_dynamodb as dynamodb
from constructs import Construct

import cdk.service.constants as constants


class ApiDbConstruct(Construct):
    def __init__(self, scope: Construct, id_: str) -> None:
        super().__init__(scope, id_)

        self.db: dynamodb.TableV2 = self._build_db(id_)
        self.idempotency_db: dynamodb.TableV2 = self._build_idempotency_table(id_)

    def _build_idempotency_table(self, id_: str) -> dynamodb.TableV2:
        table_id = f'{id_}{constants.IDEMPOTENCY_TABLE_NAME}'
        table = dynamodb.TableV2(
            self,
            table_id,
            table_name=table_id,
            partition_key=dynamodb.Attribute(name='id', type=dynamodb.AttributeType.STRING),
            billing=dynamodb.Billing.on_demand(),
            removal_policy=RemovalPolicy.DESTROY,
            time_to_live_attribute='expiration',
            point_in_time_recovery=True,
        )
        CfnOutput(self, id=constants.IDEMPOTENCY_TABLE_NAME_OUTPUT, value=table.table_name).override_logical_id(
            constants.IDEMPOTENCY_TABLE_NAME_OUTPUT
        )
        return table

    def _build_db(self, id_prefix: str) -> dynamodb.TableV2:
        table_id = f'{id_prefix}{constants.TABLE_NAME}'
        table = dynamodb.TableV2(
            self,
            table_id,
            table_name=table_id,
            partition_key=dynamodb.Attribute(name='id', type=dynamodb.AttributeType.STRING),
            billing=dynamodb.Billing.on_demand(),
            point_in_time_recovery=True,
            removal_policy=RemovalPolicy.DESTROY,
        )
        CfnOutput(self, id=constants.TABLE_NAME_OUTPUT, value=table.table_name).override_logical_id(constants.TABLE_NAME_OUTPUT)
        return table
