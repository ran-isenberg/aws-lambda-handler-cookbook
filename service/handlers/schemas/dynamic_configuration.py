from enum import Enum

from pydantic import BaseModel


# does not include feature flags part of the JSON
class MyConfiguration(BaseModel):
    region: str


class FeatureFlagsNames(Enum):
    TEN_PERCENT_CAMPAIGN = 'ten_percent_off_campaign'
