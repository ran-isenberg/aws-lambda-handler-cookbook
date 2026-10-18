from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field, HttpUrl, Json, PositiveInt


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


class Authentication(BaseModel):
    COGNITO_USER_POOL_ID: Annotated[str, Field(pattern=r'^[a-z]{2}(?:-[a-z]+)+-\d+_[A-Za-z0-9]+$')]
    COGNITO_CLIENT_ID: Annotated[str, Field(min_length=1)]
    # optional pre-fetched user pool JWKS, for functions that can't download it at runtime (no internet access)
    COGNITO_JWKS: Json[dict[str, Any]] | None = None


class MyHandlerEnvVars(Observability, DynamicConfiguration, Idempotency, Authentication):
    REST_API: HttpUrl
    ROLE_ARN: Annotated[str, Field(min_length=20, max_length=2048)]
    TABLE_NAME: Annotated[str, Field(min_length=1)]


class GetHandlerEnvVars(Observability, Authentication):
    TABLE_NAME: Annotated[str, Field(min_length=1)]


class DeleteHandlerEnvVars(Observability, Authentication):
    TABLE_NAME: Annotated[str, Field(min_length=1)]


class ListHandlerEnvVars(Observability, Authentication):
    TABLE_NAME: Annotated[str, Field(min_length=1)]
