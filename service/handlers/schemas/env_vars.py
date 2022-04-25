from typing import Literal

from pydantic import BaseModel, HttpUrl, PositiveInt, constr


class Observability(BaseModel):
    POWERTOOLS_SERVICE_NAME: constr(min_length=1)
    LOG_LEVEL: Literal['DEBUG', 'INFO', 'ERROR', 'CRITICAL', 'WARNING', 'EXCEPTION']


class DynamicConfiguration(BaseModel):
    CONFIGURATION_APP: constr(min_length=1)
    CONFIGURATION_ENV: constr(min_length=1)
    CONFIGURATION_NAME: constr(min_length=1)
    CONFIGURATION_MAX_AGE_MINUTES: PositiveInt


class MyHandlerEnvVars(Observability, DynamicConfiguration):
    REST_API: HttpUrl
    ROLE_ARN: constr(min_length=20, max_length=2048)
