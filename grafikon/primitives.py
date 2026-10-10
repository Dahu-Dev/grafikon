from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

class Attribute(BaseModel):
    model_config = ConfigDict(strict=True)
    name: str
    attType: str
    defaultValue: Any
    availableTypes: ClassVar[dict[str, type]] = {"bool": bool, "string": str, "int": int, "float": float}

    @field_validator("attType")
    @classmethod
    def check_attType(cls, attType: str) -> str:
        if attType not in cls.availableTypes:
            raise ValueError(f"Attribute type {attType!r} is not one of {list(cls.availableTypes)}")
        return attType

    @model_validator(mode="after")
    def check_default_matches_type(self) -> "Attribute":
        expected = self.availableTypes[self.attType]
        got = type(self.defaultValue)
        if got is not expected:
            raise ValueError(
                f"Default attribute value should be of type {self.attType!r}, got {got.__name__}"
            )
        return self