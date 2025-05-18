from pydantic import BaseModel


class ConditionSchema(BaseModel):
    skin_name: str
    patterns: list[str] | None = None
    float_condition: str | None = None
    price_condition: str | None = None


class ItemConditionsSchema(BaseModel):
    items: list[ConditionSchema]
