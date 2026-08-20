from dataclasses import dataclass

from app.core.config import settings
from app.models.job import JobOffer
from app.providers.france_travail import (
    FranceTravailProvider,
)
from app.services.llm.groq_job_relevance_evaluator import (
    GroqJobRelevanceEvaluator,
)
from app.services.semantic.semantic_similarity_service import (
    SemanticSimilarityService,
)


QUERY = "Machine learning"
INSEE_CODE = "75056"
LIMIT = 5


@dataclass
class EvaluationResult:
    job: JobOffer
    e5_score: float
    groq_score: float
    groq_reason: str


def build_e5_document(
    job: JobOffer,
) -> str:
    """
    Les offres brutes France Travail n'ont pas encore
    leurs skills extraits à ce stade.

    On utilise donc le titre + la description.
    """
    parts = [
        job.title.strip(),
        job.description.strip(),
    ]

    return "\n\n".join(
        part
        for part in parts
        if part
    )


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

    semantic_service = (
        SemanticSimilarityService()
    )

    groq_evaluator = (
        GroqJobRelevanceEvaluator()
    )

    print()
    print("=" * 100)
    print("REAL FRANCE TRAVAIL BENCHMARK")
    print("=" * 100)
    print(f"QUERY: {QUERY}")
    print(
        f"INSEE CODE: {INSEE_CODE}"
    )
    print(f"LIMIT: {LIMIT}")

    jobs = provider.search_jobs(
        keywords=QUERY,
        insee_code=INSEE_CODE,
        limit=LIMIT,
    )

    print(
        f"\n{len(jobs)} offres récupérées."
    )

    results: list[EvaluationResult] = []

    for index, job in enumerate(
        jobs,
        start=1,
    ):
        print()
        print(
            f"Analyse {index}/{len(jobs)} : "
            f"{job.title}"
        )

        e5_document = build_e5_document(
            job
        )

        e5_score = (
            semantic_service.similarity(
                query=QUERY,
                document=e5_document,
            )
        )

        groq_result = (
            groq_evaluator.evaluate(
                query=QUERY,
                job=job,
            )
        )

        results.append(
            EvaluationResult(
                job=job,
                e5_score=e5_score,
                groq_score=(
                    groq_result.relevance
                ),
                groq_reason=(
                    groq_result.reason
                ),
            )
        )

    # -------------------------------------------------
    # Classement E5
    # -------------------------------------------------

    by_e5 = sorted(
        results,
        key=lambda item: item.e5_score,
        reverse=True,
    )

    print("\n")
    print("=" * 100)
    print("E5-SMALL RANKING")
    print("=" * 100)

    for position, result in enumerate(
        by_e5,
        start=1,
    ):
        print(
            f"{position:>2}. "
            f"{result.e5_score:.4f} "
            f"| {result.job.title}"
            f" | {result.job.location or '-'}"
        )

    # -------------------------------------------------
    # Classement Groq
    # -------------------------------------------------

    by_groq = sorted(
        results,
        key=lambda item: item.groq_score,
        reverse=True,
    )

    print("\n")
    print("=" * 100)
    print("GROQ RANKING")
    print("=" * 100)

    for position, result in enumerate(
        by_groq,
        start=1,
    ):
        print(
            f"{position:>2}. "
            f"{result.groq_score:.3f} "
            f"| {result.job.title}"
            f" | {result.job.location or '-'}"
        )

    # -------------------------------------------------
    # Comparaison côte à côte
    # -------------------------------------------------

    e5_positions = {
        result.job.id: position
        for position, result in enumerate(
            by_e5,
            start=1,
        )
    }

    groq_positions = {
        result.job.id: position
        for position, result in enumerate(
            by_groq,
            start=1,
        )
    }

    print("\n")
    print("=" * 100)
    print("COMPARISON")
    print("=" * 100)

    print(
        f"{'E5':>4} "
        f"{'Groq':>5} "
        f"{'E5 score':>10} "
        f"{'Groq score':>11} "
        f"OFFRE"
    )

    print("-" * 100)

    for result in by_groq:
        job_id = result.job.id

        print(
            f"{e5_positions[job_id]:>4} "
            f"{groq_positions[job_id]:>5} "
            f"{result.e5_score:>10.4f} "
            f"{result.groq_score:>11.3f} "
            f"{result.job.title}"
        )

    # -------------------------------------------------
    # Raisons Groq
    # -------------------------------------------------

    print("\n")
    print("=" * 100)
    print("GROQ REASONS")
    print("=" * 100)

    for result in by_groq:
        print()
        print(
            f"{result.job.title}"
        )

        print(
            f"Location: "
            f"{result.job.location or '-'}"
        )

        print(
            f"Groq relevance: "
            f"{result.groq_score:.3f}"
        )

        print(
            f"Reason: "
            f"{result.groq_reason}"
        )


if __name__ == "__main__":
    main()