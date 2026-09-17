from pydantic import BaseModel, Field


class TailoredExperience(BaseModel):
    company: str
    selected: bool
    bullets: list[str] = Field(default_factory=list)


class TailoredProject(BaseModel):
    name: str
    selected: bool
    bullets: list[str] = Field(default_factory=list)


class TailoredResume(BaseModel):

    professional_summary: str = ""

    experience: list[TailoredExperience] = Field(
        default_factory=list
    )

    projects: list[TailoredProject] = Field(
        default_factory=list
    )

    conferences: list[str] = Field(
        default_factory=list
    )

    achievements: list[str] = Field(
        default_factory=list
    )

    skills: dict[str, list[str]] = Field(
        default_factory=dict
    )