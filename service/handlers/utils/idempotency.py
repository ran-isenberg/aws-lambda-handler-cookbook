from aws_lambda_powertools.utilities.idempotency import DynamoDBPersistenceLayer, IdempotencyConfig

from service.handlers.schemas.env_vars import Idempotency
from service.handlers.utils.env_vars_parser import get_environment_variables

IDEMPOTENCY_LAYER = DynamoDBPersistenceLayer(table_name=get_environment_variables(model=Idempotency).IDEMPOTENCY_TABLE_NAME)
IDEMPOTENCY_CONFIG = IdempotencyConfig(
    expires_after_seconds=5 * 60,  # 5 minutes
    event_key_jmespath='powertools_json(body).[customer_name, order_item_count]',
)
