from app.models.job import JobOffer
from app.services.llm.groq_job_relevance_evaluator import (
    GroqJobRelevanceEvaluator,
)


QUERY = "développeur backend"


JOBS = [
    JobOffer(
        title="Software Engineer",
        description=(
            "Conception d'APIs REST, microservices "
            "et services côté serveur."
        ),
        skills=[
            "Python",
            "FastAPI",
            "PostgreSQL",
            "REST API",
        ],
    ),
    JobOffer(
        title="Ingénieur logiciel",
        description=(
            "Développement de microservices, "
            "APIs et systèmes distribués."
        ),
        skills=[
            "Python",
            "PostgreSQL",
            "Docker",
        ],
    ),
    JobOffer(
        title="Frontend Engineer",
        description=(
            "Développement d'interfaces web "
            "et d'applications frontend."
        ),
        skills=[
            "React",
            "TypeScript",
            "CSS",
        ],
    ),
    JobOffer(
        title="DevOps Engineer",
        description=(
            "Automatisation CI/CD, Kubernetes "
            "et infrastructure cloud."
        ),
        skills=[
            "Docker",
            "Kubernetes",
            "Terraform",
        ],
    ),
]


def main() -> None:
    evaluator = GroqJobRelevanceEvaluator()

    results = []

    for job in JOBS:
        evaluation = evaluator.evaluate(
            query=QUERY,
            job=job,
        )

        results.append(
            (
                job,
                evaluation,
            )
        )

    results.sort(
        key=lambda item: item[1].relevance,
        reverse=True,
    )

    print()
    print("=" * 80)
    print(f"QUERY: {QUERY}")
    print("=" * 80)

    for position, (
        job,
        evaluation,
    ) in enumerate(
        results,
        start=1,
    ):
        print()
        print(
            f"{position}. {job.title}"
        )
        print(
            f"   relevance: "
            f"{evaluation.relevance:.3f}"
        )
        print(
            f"   reason: "
            f"{evaluation.reason}"
        )


if __name__ == "__main__":
    main()