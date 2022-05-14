from typing import List

from pydantic import BaseModel


# does not include feature flags part of the JSON
class MyConfiguration(BaseModel):
    countries: List[str]
