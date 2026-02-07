from pydantic import BaseModel


# does not include feature flags part of the JSON
class MyConfiguration(BaseModel):
    countries: list[str]
