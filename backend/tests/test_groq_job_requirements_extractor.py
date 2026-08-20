from types import SimpleNamespace

from app.models.job import JobOffer
from app.services.llm.groq_job_requirements_extractor import (
    GroqJobRequirementsExtractor,
)


class FakeCompletions:
    def create(
        self,
        **kwargs,
    ):
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content="""
{
  "hard_skills": [
    "Machine Learning",
    "RAG"
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
      "language": "English",
      "level": "B2"
    }
  ],
  "experience": {
    "min_years": 2,
    "max_years": 4,
    "context": "Machine Learning"
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
    extractor = (
        GroqJobRequirementsExtractor(
            client=FakeClient(),
            model="fake-model",
        )
    )

    job = JobOffer(
        title="AI Engineer",
        description=(
            "Développer des modèles de "
            "machine learning et les mettre "
            "en production."
        ),
    )

    result = extractor.extract(
        job
    )

    assert result.hard_skills == [
        "Machine Learning",
        "RAG",
    ]

    assert result.tools == [
        "Python",
        "AWS",
    ]

    assert (
        result.experience.min_years
        == 2
    )

    assert (
        result.experience.max_years
        == 4
    )

    assert (
        result.experience.context
        == "Machine Learning"
    )

    assert (
        result.education_level
        == "Bac+5"
    )

    assert (
        result.languages[0].language
        == "English"
    )

    assert (
        result.languages[0].level
        == "B2"
    )

    assert result.soft_skills == [
        "autonomie",
    ]

    assert result.responsibilities == [
        "Développer des modèles ML",
    ]