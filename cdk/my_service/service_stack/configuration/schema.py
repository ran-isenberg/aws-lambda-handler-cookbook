from typing import Any, Dict, Optional

from aws_lambda_powertools.utilities.feature_flags import SchemaValidator
from pydantic import BaseModel, validator


class FeatureFlagsConfiguration(BaseModel):
    features: Optional[Dict[str, Any]]

    @validator('features', pre=True)
    def validate_features(cls, value):
        validator = SchemaValidator(value)
        try:
            validator.validate()
        except Exception as exc:
            raise ValueError(str(exc))
        return value
