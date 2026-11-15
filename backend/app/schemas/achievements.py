from datetime import date
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator

NonBlank = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class AchievementCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: NonBlank
    description: str | None = None
    achievement_date: date | None = None


class AchievementUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: NonBlank | None = None
    description: str | None = None
    achievement_date: date | None = None

    @field_validator("title")
    @classmethod
    def require_value_if_sent(cls, value):
        if value is None:
            raise ValueError("This field cannot be null")
        return value


class AchievementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None
    achievement_date: date | None
