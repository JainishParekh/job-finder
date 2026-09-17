from pydantic import BaseModel


class CoverLetter(BaseModel):

    company_address: str
    person_to_address: str
    language: str
    subject: str
    greeting: str
    body: str
    closing: str
