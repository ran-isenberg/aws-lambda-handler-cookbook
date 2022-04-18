from typing import Literal

from pydantic import BaseModel, HttpUrl, constr


class MyHandlerEnvVars(BaseModel):
    REST_API: HttpUrl
    ROLE_ARN: constr(min_length=20, max_length=2048)
    POWERTOOLS_SERVICE_NAME: constr(min_length=1)
    LOG_LEVEL: Literal['DEBUG', 'INFO', 'ERROR', 'CRITICAL', 'WARNING', 'EXCEPTION']
