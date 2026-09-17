from pydantic import BaseModel, Field

class CompanyResearch(BaseModel):

    official_website: str | None = None

    company_summary: str = ""

    products_services: list[str] = Field(default_factory=list)

    technology_topics: list[str] = Field(default_factory=list)

    sources: list[str] = Field(default_factory=list)
