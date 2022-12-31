from pathlib import Path
from typing import Optional

import aws_cdk.aws_appconfig as appconfig
from constructs import Construct

from cdk.my_service.configuration.schema import FeatureFlagsConfiguration

DEFAULT_DEPLOYMENT_STRATEGY = 'AppConfig.AllAtOnce'

CUSTOM_ZERO_TIME_STRATEGY = 'zero'


class ConfigurationStore(Construct):

    def __init__(self, scope: Construct, id_: str, environment: str, service_name: str, configuration_name: str,
                 deployment_strategy_id: Optional[str] = None) -> None:
        """
        This construct should be deployed in a different repo and have its own pipeline so updates can be decoupled from
        running the service pipeline and without redeploying the service lambdas.

        Args:
            scope (Construct): The scope in which to define this construct.
            id_ (str): The scoped construct ID. Must be unique amongst siblings. If the ID includes a path separator (``/``), then it will be
                        replaced by double dash ``--``.
            environment (str): environment name. Used for loading the corresponding JSON file to upload under
                               'configuration/json/{environment}_configuration.json'
            service_name (str): application name.
            configuration_name (str): configuration name
            deployment_strategy_id (str, optional): AWS AppConfig deployment strategy.
                                                See https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-creating-deployment-strategy.html
                                                    Defaults to DEFAULT_DEPLOYMENT_STRATEGY.
        """
        super().__init__(scope, id_)

        configuration_str = self._get_and_validate_configuration(environment)

        self.config_app = appconfig.CfnApplication(
            self,
            id=f'{id_}{service_name}',
            name=f'{id_}{service_name}',
        )
        self.config_env = appconfig.CfnEnvironment(
            self,
            id=f'{id_}env',
            application_id=self.config_app.ref,
            name=environment,
        )
        self.config_profile = appconfig.CfnConfigurationProfile(
            self,
            id=f'{id_}profile',
            application_id=self.config_app.ref,
            location_uri='hosted',
            name=configuration_name,
        )
        self.hosted_cfg_version = appconfig.CfnHostedConfigurationVersion(
            self,
            f'{id_}version',
            application_id=self.config_app.ref,
            configuration_profile_id=self.config_profile.ref,
            content=configuration_str,
            content_type='application/json',
        )

        self.cfn_deployment_strategy = appconfig.CfnDeploymentStrategy(
            self,
            f'{id_}{CUSTOM_ZERO_TIME_STRATEGY}',
            deployment_duration_in_minutes=0,
            growth_factor=100,
            name=CUSTOM_ZERO_TIME_STRATEGY,
            replicate_to='NONE',
            description='zero minutes, zero bake, 100 growth all at once',
            final_bake_time_in_minutes=0,
        )

        self.app_config_deployment = appconfig.CfnDeployment(
            self,
            id=f'{id_}deploy',
            application_id=self.config_app.ref,
            configuration_profile_id=self.config_profile.ref,
            configuration_version=self.hosted_cfg_version.ref,
            deployment_strategy_id=self.cfn_deployment_strategy.ref,
            environment_id=self.config_env.ref,
        )

    def _get_and_validate_configuration(self, environment: str) -> str:
        current = Path(__file__).parent
        conf_filepath = current / (f'json/{environment}_configuration.json')
        configuration_str = conf_filepath.read_text()
        # validate configuration (check feature flags schema structure if exists)
        FeatureFlagsConfiguration.parse_raw(configuration_str)
        return configuration_str
