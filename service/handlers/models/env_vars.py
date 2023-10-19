from typing import Annotated, Literal

from pydantic import BaseModel, Field, HttpUrl, PositiveInt


class Observability(BaseModel):
    POWERTOOLS_SERVICE_NAME: Annotated[str, Field(min_length=1)]
    LOG_LEVEL: Literal['DEBUG', 'INFO', 'ERROR', 'CRITICAL', 'WARNING', 'EXCEPTION']


class Idempotency(BaseModel):
    IDEMPOTENCY_TABLE_NAME: Annotated[str, Field(min_length=1)]


class DynamicConfiguration(BaseModel):
    CONFIGURATION_APP: Annotated[str, Field(min_length=1)]
    CONFIGURATION_ENV: Annotated[str, Field(min_length=1)]
    CONFIGURATION_NAME: Annotated[str, Field(min_length=1)]
    CONFIGURATION_MAX_AGE_MINUTES: PositiveInt


class MyHandlerEnvVars(Observability, DynamicConfiguration, Idempotency):
    REST_API: HttpUrl
    ROLE_ARN: Annotated[str, Field(min_length=20, max_length=2048)]
    TABLE_NAME: Annotated[str, Field(min_length=1)]
