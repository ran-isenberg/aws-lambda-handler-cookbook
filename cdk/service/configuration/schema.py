from typing import Any, Optional

from aws_lambda_powertools.utilities.feature_flags import SchemaValidator
from pydantic import BaseModel, field_validator


class FeatureFlagsConfiguration(BaseModel):
    features: Optional[dict[str, Any]]

    @field_validator('features', mode='before')
    def validate_features(cls, value):
        validator = SchemaValidator(value)
        try:
            validator.validate()
        except Exception as exc:
            raise ValueError(str(exc))
        return value
