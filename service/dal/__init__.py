from functools import lru_cache

from service.dal.db_handler import DalHandler
from service.dal.dynamo_dal_handler import DynamoDalHandler


@lru_cache
def get_dal_handler(table_name: str) -> DalHandler:
    return DynamoDalHandler(table_name)
