from pydantic import BaseModel


def to_camel(name: str) -> str:
    return "".join([
        word.capitalize() if index > 0 else word
        for index, word in enumerate(name.split("_"))
    ])


class FixedModel(BaseModel):
    class Config:
        extra: str = "forbid"
        alias_generator = to_camel
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class Nothing(FixedModel):
    """Empty dictionary instead of values"""
