from typing import Any, Dict, TypeVar

from aws_lambda_powertools.utilities.feature_flags import AppConfigStore, FeatureFlags
from aws_lambda_powertools.utilities.feature_flags.exceptions import SchemaValidationError
from pydantic import BaseModel, ValidationError

from service.handlers.schemas.env_vars import MyHandlerEnvVars
from service.handlers.utils.env_vars_parser import get_environment_variables

Model = TypeVar('Model', bound=BaseModel)

_DYNAMIC_CONFIGURATION: FeatureFlags = None
_DEFAULT_FEATURE_FLAGS_ROOT = 'features'  # all feature flags reside in the JSON under this key


def get_dynamic_configuration() -> FeatureFlags:
    global _DYNAMIC_CONFIGURATION
    if _DYNAMIC_CONFIGURATION is None:
        # init singelton
        env_vars: MyHandlerEnvVars = get_environment_variables(model=MyHandlerEnvVars)
        conf_store = AppConfigStore(
            environment=env_vars.CONFIGURATION_ENV,
            application=env_vars.CONFIGURATION_APP,
            name=env_vars.CONFIGURATION_NAME,
            max_age=env_vars.CONFIGURATION_MAX_AGE_MINUTES,
            envelope=_DEFAULT_FEATURE_FLAGS_ROOT,
        )
        _DYNAMIC_CONFIGURATION = FeatureFlags(store=conf_store)

    return _DYNAMIC_CONFIGURATION


def parse_configuration(model: Model) -> BaseModel:
    """ Get configuration JSON and parse it into a pydantic data class.

        Args:

            model (Model): pydantic schema to load the JSON into

        Raises:
            ConfigurationStoreError, SchemaValidationError, StoreClientError: Any validation error or appconfig error that can occur

        Returns:
            BaseModel: parsed data class instance of type model
    """
    try:
        conf_json: Dict[str, Any] = get_dynamic_configuration().store.get_raw_configuration
        return model.parse_obj(conf_json)
    except (ValidationError, TypeError) as exc:
        raise SchemaValidationError(f'appconfig schema failed pydantic validation, exception={str(exc)}') from exc
