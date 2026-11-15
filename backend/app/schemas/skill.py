from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator

SkillName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class SkillCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skill_name: SkillName
    proficiency: str | None = None


class SkillUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skill_name: SkillName | None = None
    proficiency: str | None = None

    @field_validator("skill_name")
    @classmethod
    def require_name_if_sent(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("skill_name cannot be null")
        return value


class SkillRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    skill_name: str
    proficiency: str | None