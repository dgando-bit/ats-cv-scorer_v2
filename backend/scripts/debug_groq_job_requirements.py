from app.core.config import settings
from app.providers.france_travail import (
    FranceTravailProvider,
)
from app.services.llm.groq_job_requirements_extractor import (
    GroqJobRequirementsExtractor,
)


JOB_ID = "212CXFZ"


def main() -> None:
    provider = FranceTravailProvider(
        client_id=(
            settings.france_travail_client_id
        ),
        client_secret=(
            settings.france_travail_client_secret
        ),
        scope=(
            settings.france_travail_scope
        ),
    )

    extractor = (
        GroqJobRequirementsExtractor()
    )

    job = provider.get_job(
        JOB_ID
    )

    print()
    print("=" * 100)
    print("JOB")
    print("=" * 100)

    print(
        f"ID: {job.id}"
    )

    print(
        f"TITLE: {job.title}"
    )

    print(
        f"LOCATION: {job.location}"
    )

    requirements = extractor.extract(
        job
    )

    print()
    print("=" * 100)
    print("REQUIREMENTS")
    print("=" * 100)

    print(
        requirements.model_dump_json(
            indent=2
        )
    )


if __name__ == "__main__":
    main()