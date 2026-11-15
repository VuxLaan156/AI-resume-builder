from datetime import date
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator

NonBlank = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class CertificationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: NonBlank
    issuing_body: NonBlank
    issue_date: date | None = None


class CertificationUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: NonBlank | None = None
    issuing_body: NonBlank | None = None
    issue_date: date | None = None

    @field_validator("name", "issuing_body")
    @classmethod
    def require_value_if_sent(cls, value):
        if value is None:
            raise ValueError("This field cannot be null")
        return value


class CertificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    issuing_body: str
    issue_date: date | None
