from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator

ProjectName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class ProjectCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_name: ProjectName
    description: str | None = None


class ProjectUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_name: ProjectName | None = None
    description: str | None = None

    @field_validator("project_name")
    @classmethod
    def require_name_if_sent(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("project_name cannot be null")
        return value


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_name: str
    description: str | None
