from pydantic import BaseModel


class FixedModel(BaseModel):
    class Config:
        extra: str = "forbid"
