from aws_cdk import Duration, RemovalPolicy
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion
from aws_cdk.aws_logs import RetentionDays
from constructs import Construct

import cdk.service.constants as constants
from cdk.service.api_db_construct import ApiDbConstruct


class ApiConstruct(Construct):
    def __init__(self, scope: Construct, id_: str) -> None:
        super().__init__(scope, id_)
        self.id_ = id_
        self.api_db = ApiDbConstruct(self, f'{id_}db')
        self.lambda_role = self._build_lambda_role(self.api_db.db, self.api_db.idempotency_db)
        self.common_layer = self._build_common_layer()
        self.create_order_func = self._add_post_lambda_integration(self.lambda_role, self.api_db.db, self.api_db.idempotency_db)

    def _build_lambda_role(self, db: dynamodb.TableV2, idempotency_table: dynamodb.TableV2) -> iam.Role:
        return iam.Role(
            self,
            constants.SERVICE_ROLE_ARN,
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            inline_policies={
                'dynamodb_db': iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=['dynamodb:PutItem', 'dynamodb:GetItem'],
                            resources=[db.table_arn],
                            effect=iam.Effect.ALLOW,
                        )
                    ]
                ),
                'idempotency_table': iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=['dynamodb:PutItem', 'dynamodb:GetItem', 'dynamodb:UpdateItem', 'dynamodb:DeleteItem'],
                            resources=[idempotency_table.table_arn],
                            effect=iam.Effect.ALLOW,
                        )
                    ]
                ),
            },
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name=(f'service-role/{constants.LAMBDA_BASIC_EXECUTION_ROLE}'))
            ],
        )

    def _build_common_layer(self) -> PythonLayerVersion:
        return PythonLayerVersion(
            self,
            f'{self.id_}{constants.LAMBDA_LAYER_NAME}',
            entry=constants.COMMON_LAYER_BUILD_FOLDER,
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_12],
            removal_policy=RemovalPolicy.DESTROY,
        )

    def _add_post_lambda_integration(
        self,
        role: iam.Role,
        db: dynamodb.TableV2,
        idempotency_table: dynamodb.TableV2,
    ) -> _lambda.Function:
        lambda_function = _lambda.Function(
            self,
            constants.CREATE_LAMBDA,
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset(constants.BUILD_FOLDER),
            handler='service.handlers.handle_create_order.lambda_handler',
            environment={
                constants.POWERTOOLS_SERVICE_NAME: constants.SERVICE_NAME,  # for logger, tracer and metrics
                constants.POWER_TOOLS_LOG_LEVEL: 'INFO',  # for logger
                'TABLE_NAME': db.table_name,
                'IDEMPOTENCY_TABLE_NAME': idempotency_table.table_name,
            },
            tracing=_lambda.Tracing.ACTIVE,
            retry_attempts=0,
            timeout=Duration.seconds(constants.API_HANDLER_LAMBDA_TIMEOUT),
            memory_size=constants.API_HANDLER_LAMBDA_MEMORY_SIZE,
            layers=[self.common_layer],
            role=role,
            log_retention=RetentionDays.ONE_DAY,
            log_format=_lambda.LogFormat.JSON.value,
            system_log_level=_lambda.SystemLogLevel.INFO.value,
        )

        return lambda_function
