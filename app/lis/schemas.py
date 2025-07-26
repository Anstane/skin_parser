from pydantic import BaseModel


class ConditionSchema(BaseModel):
    skin_name: str
    patterns: list[str] | None = None
    float_condition: str | None = None
    price_condition: str | None = None
    ready_to_buy: bool = False


class ItemConditionsSchema(BaseModel):
    items: list[ConditionSchema]
