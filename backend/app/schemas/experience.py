from datetime import date
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator

NonBlank = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class ExperienceCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_title: NonBlank
    company_name: NonBlank
    description: str | None = None
    start_date: date
    end_date: date | None = None


class ExperienceUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_title: NonBlank | None = None
    company_name: NonBlank | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None

    @field_validator("job_title", "company_name", "start_date")
    @classmethod
    def require_value_if_sent(cls, value):
        if value is None:
            raise ValueError("This field cannot be null")
        return value


class ExperienceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_title: str
    company_name: str
    description: str | None
    start_date: date
    end_date: date | None
