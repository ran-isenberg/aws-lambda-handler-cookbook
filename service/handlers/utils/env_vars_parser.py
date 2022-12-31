import os
from functools import lru_cache
from typing import Any, Type, TypeVar

from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from pydantic import BaseModel, ValidationError

Model = TypeVar('Model', bound=BaseModel)


@lru_cache
def __parse_model(model: Type[Model]) -> Model:
    try:
        return model.parse_obj(os.environ)
    except (ValidationError, TypeError) as exc:
        raise ValueError(f'failed to load environment variables, exception={str(exc)}') from exc


@lambda_handler_decorator
def init_environment_variables(handler, event, context, model: Model) -> Any:
    __parse_model(model)
    return handler(event, context)


def get_environment_variables(model: Type[Model]) -> Model:
    return __parse_model(model)
