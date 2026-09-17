from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

# ============================================================
# BASICS
# ============================================================


class Location(BaseModel):
    address: Optional[str] = None
    city: Optional[str] = None
    countryCode: Optional[str] = None


class ProfileLink(BaseModel):
    network: str
    url: str


class Basics(BaseModel):
    name: str

    image: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None

    location: Optional[Location] = None

    profiles: list[ProfileLink] = Field(default_factory=list)


# ============================================================
# EDUCATION
# ============================================================


class Education(BaseModel):
    institution: str
    location: Optional[str] = None

    area: str
    studyType: str

    score: Optional[str] = None

    startDate: str
    endDate: Optional[str] = None


# ============================================================
# WORK EXPERIENCE
# ============================================================


class WorkExperience(BaseModel):
    company: str
    position: str
    location: Optional[str] = None

    startDate: str
    endDate: Optional[str] = None

    technologies: list[str] = Field(default_factory=list)

    highlights: list[str] = Field(default_factory=list)


# ============================================================
# PROJECTS
# ============================================================


class Project(BaseModel):
    name: str

    context: Optional[str] = None

    startDate: str
    endDate: Optional[str] = None

    technologies: list[str] = Field(default_factory=list)

    highlights: list[str] = Field(default_factory=list)


# ============================================================
# CONFERENCES
# ============================================================


class Conference(BaseModel):
    title: str

    url: Optional[str] = None

    startDate: str
    endDate: Optional[str] = None

    highlights: list[str] = Field(default_factory=list)


# ============================================================
# ACHIEVEMENTS
# ============================================================


class Achievement(BaseModel):
    title: str
    description: str


# ============================================================
# SKILLS
# ============================================================


class Skills(BaseModel):
    programming_languages: list[str] = Field(
        default_factory=list, alias="Programmiersprachen"
    )

    frameworks_libraries: list[str] = Field(
        default_factory=list, alias="Frameworks & Bibliotheken"
    )

    tools_devops: list[str] = Field(
        default_factory=list, alias="Entwicklungswerkzeuge & DevOps"
    )

    model_config = ConfigDict(populate_by_name=True)


# ============================================================
# LANGUAGES
# ============================================================


class Language(BaseModel):
    language: str
    fluency: str


# ============================================================
# COMPLETE CANDIDATE PROFILE
# ============================================================


class CandidateProfile(BaseModel):

    basics: Basics

    education: list[Education] = Field(default_factory=list)

    work: list[WorkExperience] = Field(default_factory=list)

    projects: list[Project] = Field(default_factory=list)

    conferences: list[Conference] = Field(default_factory=list)

    achievements: list[Achievement] = Field(default_factory=list)

    skills: Optional[Skills] = None

    languages: list[Language] = Field(default_factory=list)
