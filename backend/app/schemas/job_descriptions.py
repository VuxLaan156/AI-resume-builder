from decimal import Decimal
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, PositiveInt, StringConstraints, model_validator

NonBlank = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
NonNegativeNumber = Annotated[Decimal, Field(ge=0, allow_inf_nan=False)]
RequirementLevel = Literal["required", "preferred", "unspecified"]


class SourceEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_quote: NonBlank
    page_number: PositiveInt | None = None


class SkillEvidence(SourceEvidence):
    name: NonBlank


class Qualification(SourceEvidence):
    text: NonBlank
    level: RequirementLevel = "unspecified"


class ExperienceRequirement(Qualification):
    area: NonBlank | None = None
    min_years: NonNegativeNumber | None = None
    max_years: NonNegativeNumber | None = None

    @model_validator(mode="after")
    def validate_years(self) -> Self:
        if self.min_years is not None and self.max_years is not None:
            if self.max_years < self.min_years:
                raise ValueError("max_years must be at least min_years")
        return self


class JDAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: NonBlank | None = None
    title_evidence: SourceEvidence | None = None
    required_skills: list[SkillEvidence] = Field(default_factory=list)
    preferred_skills: list[SkillEvidence] = Field(default_factory=list)
    unspecified_skills: list[SkillEvidence] = Field(default_factory=list)
    experience_requirements: list[ExperienceRequirement] = Field(default_factory=list)
    education_requirements: list[Qualification] = Field(default_factory=list)
    certification_requirements: list[Qualification] = Field(default_factory=list)
    language_requirements: list[Qualification] = Field(default_factory=list)
