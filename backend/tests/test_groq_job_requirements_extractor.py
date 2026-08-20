from types import SimpleNamespace

from app.models.job import JobOffer
from app.services.llm.groq_job_requirements_extractor import (
    GroqJobRequirementsExtractor,
)


class FakeCompletions:
    def create(self, **kwargs):
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content="""
{
  "hard_skills": [
    "machine learning",
    "feature engineering"
  ],
  "tools": [
    "Python",
    "AWS"
  ],
  "soft_skills": [
    "autonomie"
  ],
  "languages": [
    {
      "language": "anglais",
      "level": "B2"
    }
  ],
  "experience": {
    "min_years": 2,
    "max_years": 4
  },
  "education_level": "Bac+5",
  "certifications": [],
  "responsibilities": [
    "Développer des modèles ML"
  ]
}
"""
                    )
                )
            ]
        )


class FakeClient:
    def __init__(self):
        self.chat = SimpleNamespace(
            completions=FakeCompletions()
        )


def test_extract_job_requirements():
    extractor = GroqJobRequirementsExtractor(
        client=FakeClient(),
        model="fake-model",
    )

    job = JobOffer(
        title="AI Engineer",
        description=(
            "Développer des modèles de machine learning "
            "et les mettre en production."
        ),
    )

    result = extractor.extract(job)

    assert result.hard_skills == [
        "machine learning",
        "feature engineering",
    ]

    assert result.tools == [
        "Python",
        "AWS",
    ]

    assert result.experience.min_years == 2
    assert result.experience.max_years == 4

    assert result.education_level == "Bac+5"

    assert (
        result.languages[0].language
        == "anglais"
    )

    assert (
        result.languages[0].level
        == "B2"
    )