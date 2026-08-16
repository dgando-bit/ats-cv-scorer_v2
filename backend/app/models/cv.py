from pydantic import BaseModel, Field


class Contact(BaseModel):
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    website: str | None = None

class Experience(BaseModel):
    company: str | None = None
    role: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    description: list[str] = Field(default_factory=list)


class Education(BaseModel):
    institution: str | None = None
    degree: str | None = None
    year: str | None = None


class CV(BaseModel):
    candidate_name: str | None = None
    title: str | None = None

    contact: Contact = Field(default_factory=Contact)

    profile: str | None = None

    experiences: list[Experience] = Field(
        default_factory=list
    )

    education: list[Education] = Field(
        default_factory=list
    )

    skills: list[str] = Field(
        default_factory=list
    )

    soft_skills: list[str] = Field(
        default_factory=list
    )

    tools: list[str] = Field(
        default_factory=list
    )

    languages: list[str] = Field(
        default_factory=list
    )