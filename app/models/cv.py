from pydantic import BaseModel, Field


class PersonalInfo(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    urls: list[str] = Field(default_factory=list)


class ExperienceItem(BaseModel):
    company: str | None = None
    role: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    description: list[str] = Field(default_factory=list)


class EducationItem(BaseModel):
    degree: str | None = None
    institution: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None


class LanguageItem(BaseModel):
    language: str
    level: str | None = None


class CVProfile(BaseModel):
    personal_info: PersonalInfo = Field(
        default_factory=PersonalInfo
    )

    profile: str | None = None

    experiences: list[ExperienceItem] = Field(
        default_factory=list
    )

    education: list[EducationItem] = Field(
        default_factory=list
    )

    skills: list[str] = Field(
        default_factory=list
    )

    soft_skills: list[str] = Field(
        default_factory=list
    )

    languages: list[LanguageItem] = Field(
        default_factory=list
    )