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
    def __init__(
        self,
    ):
        self.chat = SimpleNamespace(
            completions=FakeCompletions()
        )


class FakeCompanyExperienceCompletions:
    """
    Simule une erreur du LLM :

    le modèle a interprété les 55 ans d'expérience
    de l'entreprise comme une exigence candidat.
    """

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
    "Machine Learning"
  ],
  "tools": [],
  "soft_skills": [],
  "languages": [],
  "experience": {
    "min_years": 55,
    "max_years": null,
    "context": "industrial projects"
  },
  "education_level": null,
  "certifications": [],
  "responsibilities": []
}
"""
                    )
                )
            ]
        )


class FakeCompanyExperienceClient:
    def __init__(
        self,
    ):
        self.chat = SimpleNamespace(
            completions=(
                FakeCompanyExperienceCompletions()
            )
        )


class CapturingCompletions:
    """
    Permet de vérifier que notre prompt contient
    bien les règles nécessaires.
    """

    def __init__(
        self,
    ):
        self.kwargs = None

    def create(
        self,
        **kwargs,
    ):
        self.kwargs = kwargs

        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content="""
{
  "hard_skills": [],
  "tools": [],
  "soft_skills": [],
  "languages": [],
  "experience": {
    "min_years": null,
    "max_years": null,
    "context": null
  },
  "education_level": null,
  "certifications": [],
  "responsibilities": []
}
"""
                    )
                )
            ]
        )


class CapturingClient:
    def __init__(
        self,
    ):
        self.completions = (
            CapturingCompletions()
        )

        self.chat = SimpleNamespace(
            completions=self.completions
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


def test_implausible_company_experience_is_removed():
    extractor = (
        GroqJobRequirementsExtractor(
            client=(
                FakeCompanyExperienceClient()
            ),
            model="fake-model",
        )
    )

    job = JobOffer(
        title=(
            "Machine Learning Engineer"
        ),
        description=(
            "L'entreprise possède plus de "
            "55 ans d'expérience dans des "
            "projets industriels complexes."
        ),
    )

    result = extractor.extract(
        job
    )

    assert (
        result.experience.min_years
        is None
    )

    assert (
        result.experience.max_years
        is None
    )

    assert (
        result.experience.context
        is None
    )


def test_prompt_distinguishes_company_experience_from_candidate_experience():
    client = CapturingClient()

    extractor = (
        GroqJobRequirementsExtractor(
            client=client,
            model="fake-model",
        )
    )

    job = JobOffer(
        title="ML Engineer",
        description=(
            "Plus de 55 ans d'expérience "
            "dans des projets industriels."
        ),
    )

    extractor.extract(
        job
    )

    messages = (
        client.completions
        .kwargs["messages"]
    )

    system_prompt = (
        messages[0]["content"]
        .lower()
    )

    assert (
        "company"
        in system_prompt
    )

    assert (
        "candidate"
        in system_prompt
    )

    assert (
        "55 years"
        in system_prompt
    )

    assert (
        "must not"
        in system_prompt
    )