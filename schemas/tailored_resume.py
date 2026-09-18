from pydantic import BaseModel, Field
from typing import Optional

class Location(BaseModel):
    city: str = Field(description="Name of the city")
    country: str = Field(description="Nam eof the country")
    
class Address(BaseModel):
    street: str
    city: str
    country: str

class TailoredHeader(BaseModel):
    full_name: str
    profile_image: str
    address: Address
    phone_number: str
    email: str
    personal_portfolio_website: str
    linkedin: str
    github: str

class TailoredExperience(BaseModel):
    company: str
    duration: str
    location: Location
    bullets: list[str] = Field(default_factory=list, description="List will have at least 2 or 3 elements which are in turn information on experience")

class TailoredProject(BaseModel):
    name: str
    organization: str = Field(default="Personal Project", description="States that in association of which organization was the project made.")
    duration: str = Field(description="Time duration in which the project was made")
    bullets: list[str] = Field(default_factory=list, description="List will have at least 2 or 3 elements which are in turn information on projects")

class TailoredConference(BaseModel):
    topic: str = Field(description="Name of the topic for which was presented in the conference")
    date: str = Field(description="Date on which conference was held and corresponding was presented")
    bullets: list[str] = Field(default_factory=list, description="List will have at least one or more points describing about topic of the conference paper published.")
    organization: str = Field(description="Name of the organization for which the conference paper was published.")
    
class TailoredAchievement(BaseModel):
    name: str = Field(description="Main title about what was the achievement")
    datetime: str = Field(description="Date on which the achievement was achieved")
    description: Optional[str] = Field(description="Single line describing achievement in short. It is optional field so, depending on job description can be added or omitted.")

class TailoredResume(BaseModel):

    profile_header: TailoredHeader

    experience: list[TailoredExperience] = Field(
        default_factory=list
    )

    projects: list[TailoredProject] = Field(
        default_factory=list
    )

    conferences: list[TailoredConference] = Field(
        default_factory=list
    )

    achievements: list[TailoredAchievement] = Field(
        default_factory=list
    )

    skills: dict[str, list[str]] = Field(
        default_factory=dict
    )