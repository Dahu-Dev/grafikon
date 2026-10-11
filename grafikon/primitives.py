from typing import Any, ClassVar, Optional
from uuid import uuid4, UUID

from pydantic import BaseModel, ConfigDict, field_validator, model_validator, Field

class Attribute(BaseModel):
    model_config = ConfigDict(strict=True)
    name: str
    attType: str
    value: Any = None
    types: ClassVar[dict[str, type]] = {"bool": bool, "string": str, "int": int, "float": float}

    @field_validator("attType", mode="after")
    @classmethod
    def check_attType(cls, attType: str) -> str:
        if attType not in cls.types:
            raise ValueError(f"Attribute type {attType!r} is not one of {list(cls.types)}")
        return attType

    @model_validator(mode="after")
    def check_value_matches_type(self) -> "Attribute":
        expected = self.types[self.attType]
        got = type(self.value)
        if got is not expected and self.value is not None:
            raise ValueError(
                f"Attribute value should be of type {self.attType!r}, got {got.__name__}"
            )
        return self

class Layer(BaseModel):
    label: str
    parent: Optional[UUID|str] = None
    children: list[UUID|str] = Field(default_factory=list)
    id: UUID|str = Field(default_factory=uuid4)

    @model_validator(mode="after")
    def check_if_root(self) -> "Layer":
        if self.parent == None and self.label != self.id and self.id != "0":
            raise ValueError("Only the root node can have no parent")
        return self

class Entity(BaseModel):
    layer: Layer
    attributeValues: dict[str, Attribute] = Field(default_factory=dict)
    id: UUID = Field(default_factory=uuid4)

class Coordinate(BaseModel):
    x: float
    y: float
    z: Optional[float] = None

    @property
    def is_3d(self) -> bool:
        return self.z is not None

    @property
    def xy(self) -> tuple[float, float]:
        return self.x, self.y

    @property
    def xyz(self) -> tuple[float, float, float|None]:
        return self.x, self.y, self.z

class Point(Entity):
    coordinate: Coordinate
    pointStyle: str = "dot"
    pointStyles: ClassVar[tuple[str]] = ("dot",)

    @field_validator("pointStyle", mode="after")
    @classmethod
    def check_attType(cls, pointStyle: str) -> str:
        if pointStyle not in cls.pointStyles:
            raise ValueError(f"The specified point style {pointStyle!r} is not one of {cls.pointStyles}")
        return pointStyle


class Polyline(Entity):
    points: list[Point]
    closed: bool = False

    @field_validator("points", mode="after")
    @classmethod
    def check_points(cls, points: list[Point]) -> list[Point]:
        if len(points) < 2:
            raise ValueError("A polyline must have 2 or more points.")
        return points