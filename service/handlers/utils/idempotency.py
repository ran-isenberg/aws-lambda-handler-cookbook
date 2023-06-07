from aws_lambda_powertools.utilities.idempotency import DynamoDBPersistenceLayer, IdempotencyConfig

IDEMPOTENCY_LAYER = DynamoDBPersistenceLayer(table_name='IdempotencyTable')
IDEMPOTENCY_CONFIG = IdempotencyConfig(
    use_local_cache=True,
    expires_after_seconds=5 * 60,  # 5 minutes
    event_key_jmespath='powertools_json(body).[customer_name, order_item_count]',
)
