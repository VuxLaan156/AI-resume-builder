from datetime import date
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator

NonBlank = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class EducationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    institution: NonBlank
    degree: NonBlank
    graduation_date: date | None = None


class EducationUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    institution: NonBlank | None = None
    degree: NonBlank | None = None
    graduation_date: date | None = None

    @field_validator("institution", "degree")
    @classmethod
    def require_value_if_sent(cls, value):
        if value is None:
            raise ValueError("This field cannot be null")
        return value


class EducationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    institution: str
    degree: str
    graduation_date: date | None
