from pydantic import BaseModel, Field


class JobMatch(BaseModel):

    match_score: int = Field(
        ge=0,
        le=100,
    )

    match_reasoning: str

    relevant_experience: list[str] = Field(
        default_factory=list,
    )

    relevant_projects: list[str] = Field(
        default_factory=list,
    )

    relevant_skills: list[str] = Field(
        default_factory=list,
    )

    missing_requirements: list[str] = Field(
        default_factory=list,
    )

    tailored_bullets: list[str] = Field(
        default_factory=list,
        max_length=3,
    )
