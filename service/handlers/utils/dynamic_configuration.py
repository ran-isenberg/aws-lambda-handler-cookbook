from typing import Any, Dict, Type, TypeVar, Union

from aws_lambda_powertools.utilities.feature_flags import AppConfigStore, FeatureFlags
from aws_lambda_powertools.utilities.feature_flags.exceptions import SchemaValidationError
from pydantic import BaseModel, ValidationError

from service.handlers.schemas.env_vars import DynamicConfiguration
from service.handlers.utils.env_vars_parser import get_environment_variables

Model = TypeVar('Model', bound=BaseModel)

_DYNAMIC_CONFIGURATION: Union[FeatureFlags, None] = None
_DEFAULT_FEATURE_FLAGS_ROOT = 'features'  # all feature flags reside in the JSON under this key


def get_dynamic_configuration_store() -> FeatureFlags:
    """ getter for singleton dynamic configuration getter API

    Returns:
        FeatureFlags: see https://awslabs.github.io/aws-lambda-powertools-python/latest/utilities/feature_flags/
    """
    global _DYNAMIC_CONFIGURATION
    if _DYNAMIC_CONFIGURATION is None:
        # init singleton
        env_vars: DynamicConfiguration = get_environment_variables(model=DynamicConfiguration)
        conf_store = AppConfigStore(
            environment=env_vars.CONFIGURATION_ENV,
            application=env_vars.CONFIGURATION_APP,
            name=env_vars.CONFIGURATION_NAME,
            max_age=env_vars.CONFIGURATION_MAX_AGE_MINUTES,
            envelope=_DEFAULT_FEATURE_FLAGS_ROOT,
        )
        _DYNAMIC_CONFIGURATION = FeatureFlags(store=conf_store)

    return _DYNAMIC_CONFIGURATION


def parse_configuration(model: Type[Model]) -> Type[BaseModel]:
    """ Get configuration JSON from AWS AppConfig and parse it into a pydantic data-class instance.
        Args:
            model (Model): pydantic schema to load the JSON into
        Raises:
            ConfigurationStoreError, SchemaValidationError, StoreClientError: Any validation error or appconfig error that can occur
        Returns:
            BaseModel: parsed data class instance of type model
    """
    try:
        conf_json: Dict[str, Any] = get_dynamic_configuration_store().store.get_raw_configuration
        return model.parse_obj(conf_json)  # type: ignore
    except (ValidationError, TypeError) as exc:
        raise SchemaValidationError(f'appconfig schema failed pydantic validation, exception={str(exc)}') from exc
