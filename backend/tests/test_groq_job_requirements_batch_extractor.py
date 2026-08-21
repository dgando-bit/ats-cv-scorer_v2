from types import SimpleNamespace

from app.models.job import JobOffer
from app.services.llm.groq_job_requirements_batch_extractor import (
    GroqJobRequirementsBatchExtractor,
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
  "requirements": [
    {
      "hard_skills": [
        "Accueil patient",
        "Terminologie médicale"
      ],
      "tools": [
        "Pack Office"
      ],
      "soft_skills": [
        "Organisation",
        "Aisance relationnelle"
      ],
      "languages": [],
      "experience": {
        "min_years": null,
        "max_years": null,
        "context": null
      },
      "education_level": null,
      "certifications": [],
      "responsibilities": [
        "Accueillir les patients",
        "Gérer les dossiers médicaux"
      ]
    },
    {
      "hard_skills": [
        "Machine Learning",
        "MLOps"
      ],
      "tools": [
        "Python",
        "Docker"
      ],
      "soft_skills": [
        "Collaboration"
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
        "Develop ML models",
        "Deploy models to production"
      ]
    }
  ]
}
"""
                    )
                )
            ]
        )


class FakeClient:
    def __init__(
        self,
    ):
        self.chat = SimpleNamespace(
            completions=FakeCompletions()
        )


def test_extract_job_requirements_batch():
    extractor = (
        GroqJobRequirementsBatchExtractor(
            client=FakeClient(),
            model="fake-model",
        )
    )

    jobs = [
        JobOffer(
            id="1",
            title="Secrétaire médicale",
            description=(
                "Accueil des patients, gestion des "
                "dossiers médicaux et maîtrise du "
                "Pack Office."
            ),
        ),
        JobOffer(
            id="2",
            title="Machine Learning Engineer",
            description=(
                "Développer et industrialiser des "
                "modèles de Machine Learning avec "
                "Python et Docker."
            ),
        ),
    ]

    results = extractor.extract(
        jobs
    )

    assert len(
        results
    ) == 2

    first = results[0]

    assert (
        "Accueil patient"
        in first.hard_skills
    )

    assert (
        "Terminologie médicale"
        in first.hard_skills
    )

    assert (
        "Pack Office"
        in first.tools
    )

    assert (
        "Organisation"
        in first.soft_skills
    )

    assert (
        first.education_level
        is None
    )

    second = results[1]

    assert (
        "Machine Learning"
        in second.hard_skills
    )

    assert (
        "MLOps"
        in second.hard_skills
    )

    assert (
        "Python"
        in second.tools
    )

    assert (
        "Docker"
        in second.tools
    )

    assert (
        second.experience.min_years
        == 2
    )

    assert (
        second.experience.max_years
        == 4
    )

    assert (
        second.education_level
        == "Bac+5"
    )

    assert (
        second.languages[0].language
        == "English"
    )

    assert (
        second.languages[0].level
        == "B2"
    )