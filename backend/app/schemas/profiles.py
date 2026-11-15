from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProfileCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str | None = None
    contact_info: dict[str, Any] = Field(default_factory=dict)


class ProfileUpdate(ProfileCreate):
    pass


class ProfileRead(ProfileCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID