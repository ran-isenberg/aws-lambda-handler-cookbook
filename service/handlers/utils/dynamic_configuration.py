from typing import TypeVar, Union

from aws_lambda_env_modeler import get_environment_variables
from aws_lambda_powertools.utilities.feature_flags import AppConfigStore, FeatureFlags
from pydantic import BaseModel

from service.handlers.models.env_vars import DynamicConfiguration
from service.models.exceptions import DynamicConfigurationException

Model = TypeVar('Model', bound=BaseModel)

_DYNAMIC_CONFIGURATION: Union[FeatureFlags, None] = None
_DEFAULT_FEATURE_FLAGS_ROOT = 'features'  # all feature flags reside in the JSON under this key


def get_configuration_store() -> FeatureFlags:
    """getter for singleton dynamic configuration getter API

    Returns:
        FeatureFlags: see https://docs.powertools.aws.dev/lambda-python/latest/utilities/feature_flags/
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


def parse_configuration(model: type[Model]) -> Model:
    """Get configuration JSON from AWS AppConfig and parse it into a pydantic data-class instance.
    Args:
        model (Model): pydantic schema to load the JSON into
    Raises:
        DynamicConfigurationException: Any validation error or appconfig error that can occur
    Returns:
        BaseModel: parsed data class instance of type model
    """
    try:
        conf_json = get_configuration_store().store.get_raw_configuration
        return model.model_validate(conf_json)
    except Exception as exc:
        raise DynamicConfigurationException(f'appconfig schema failed pydantic validation, exception={str(exc)}') from exc
